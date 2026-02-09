#include <algorithm>
#include <cmath>
#include <fstream>
#include <iostream>
#include <optional>
#include <regex>
#include <set>
#include <sstream>
#include <string>
#include <vector>

namespace {
std::string read_file(const std::string &path) {
    std::ifstream file(path);
    if (!file) {
        return "";
    }
    std::ostringstream buffer;
    buffer << file.rdbuf();
    return buffer.str();
}

std::string json_escape(const std::string &input) {
    std::string out;
    out.reserve(input.size());
    for (char c : input) {
        switch (c) {
        case '\\':
            out += "\\\\";
            break;
        case '"':
            out += "\\\"";
            break;
        case '\n':
            out += "\\n";
            break;
        case '\r':
            out += "\\r";
            break;
        case '\t':
            out += "\\t";
            break;
        default:
            out += c;
            break;
        }
    }
    return out;
}

std::vector<std::string> extract_objects(const std::string &json) {
    std::vector<std::string> objects;
    int depth = 0;
    bool in_string = false;
    bool escape = false;
    size_t start = 0;

    for (size_t i = 0; i < json.size(); ++i) {
        char c = json[i];
        if (escape) {
            escape = false;
            continue;
        }
        if (c == '\\') {
            if (in_string) {
                escape = true;
            }
            continue;
        }
        if (c == '"') {
            in_string = !in_string;
            continue;
        }
        if (in_string) {
            continue;
        }
        if (c == '{') {
            if (depth == 0) {
                start = i;
            }
            ++depth;
        } else if (c == '}') {
            --depth;
            if (depth == 0) {
                objects.push_back(json.substr(start, i - start + 1));
            }
        }
    }

    return objects;
}

std::optional<std::string> extract_string(const std::string &object,
                                          const std::vector<std::string> &keys) {
    for (const auto &key : keys) {
        std::regex pattern("\\\"" + key + "\\\"\\s*:\\s*\\\"([^\\\"]*)\\\"");
        std::smatch match;
        if (std::regex_search(object, match, pattern)) {
            return match[1].str();
        }
    }
    return std::nullopt;
}

std::optional<double> extract_number(const std::string &object,
                                     const std::vector<std::string> &keys) {
    for (const auto &key : keys) {
        std::regex pattern("\\\"" + key + "\\\"\\s*:\\s*([-+]?(?:\\d*\\.?\\d+|\\d+)(?:[eE][-+]?\\d+)?)");
        std::smatch match;
        if (std::regex_search(object, match, pattern)) {
            try {
                return std::stod(match[1].str());
            } catch (const std::exception &) {
                return std::nullopt;
            }
        }
    }
    return std::nullopt;
}

std::optional<double> extract_number(const std::string &object,
                                     const std::vector<std::string> &keys1,
                                     const std::vector<std::string> &keys2) {
    if (auto value = extract_number(object, keys1)) {
        return value;
    }
    return extract_number(object, keys2);
}

void print_error(const std::string &message) {
    std::cout << "{\"error\":\"" << json_escape(message) << "\"}";
}
} // namespace

int main(int argc, char *argv[]) {
    if (argc < 4) {
        print_error("Usage: calculator <db_path> <mode> <d> [D] [B]");
        return 1;
    }

    std::string db_path = argv[1];
    std::string mode = argv[2];
    double user_d = std::stod(argv[3]);
    double user_D = 0.0;
    double user_B = 0.0;

    if (mode == "bearing") {
        if (argc < 6) {
            print_error("Bearing search requires d D B");
            return 1;
        }
        user_D = std::stod(argv[4]);
        user_B = std::stod(argv[5]);
    }

    std::string content = read_file(db_path);
    if (content.empty()) {
        print_error("Database file not found or empty");
        return 1;
    }

    auto objects = extract_objects(content);
    if (objects.empty()) {
        print_error("No records found in database");
        return 1;
    }

    const std::vector<std::string> type_keys = {"type"};
    const std::vector<std::string> model_keys = {"model", "Model"};
    const std::vector<std::string> desc_keys = {"purpose", "description", "special_features", "specialfeatures"};

    const std::vector<std::string> bearing_d_keys = {"d"};
    const std::vector<std::string> bearing_d_alt = {"inner_diameter", "innerdiameter", "inner", "id", "di"};
    const std::vector<std::string> bearing_D_keys = {"D"};
    const std::vector<std::string> bearing_D_alt = {"outer_diameter", "outerdiameter", "outer", "od"};
    const std::vector<std::string> bearing_B_keys = {"B", "b"};
    const std::vector<std::string> bearing_B_alt = {"width", "w"};

    const std::vector<std::string> housing_d_keys = {"d", "shaft_diameter", "bearing_bore"};
    const std::vector<std::string> housing_d_alt = {"inner_diameter", "innerdiameter", "shaft_diameter", "shaftdiameter", "bearing_bore", "bearingbore"};

    std::set<std::pair<std::string, std::string>> results;

    for (const auto &object : objects) {
        auto type = extract_string(object, type_keys);
        if (!type || (mode == "bearing" && *type != "bearing") || (mode == "housing" && *type != "housing")) {
            continue;
        }

        bool match = false;
        if (mode == "bearing") {
            auto d_val = extract_number(object, bearing_d_keys, bearing_d_alt);
            auto D_val = extract_number(object, bearing_D_keys, bearing_D_alt);
            auto B_val = extract_number(object, bearing_B_keys, bearing_B_alt);
            if (!d_val || !D_val || !B_val) {
                continue;
            }
            match = std::abs(*d_val - user_d) < 0.2 && std::abs(*D_val - user_D) < 0.2 &&
                    std::abs(*B_val - user_B) < 1.0;
        } else {
            auto d_val = extract_number(object, housing_d_keys, housing_d_alt);
            if (!d_val) {
                continue;
            }
            match = std::abs(*d_val - user_d) < 0.2;
        }

        if (match) {
            std::string model = extract_string(object, model_keys).value_or("N/A");
            std::string desc = extract_string(object, desc_keys).value_or("");
            results.emplace(model, desc);
        }
    }

    std::cout << "{\"results\":[";
    bool first = true;
    for (const auto &entry : results) {
        if (!first) {
            std::cout << ',';
        }
        first = false;
        std::cout << "{\"model\":\"" << json_escape(entry.first) << "\",\"description\":\""
                  << json_escape(entry.second) << "\"}";
    }
    std::cout << "]}";
    return 0;
}
