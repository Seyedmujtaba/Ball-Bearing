#include <iostream>
#include <fstream>
#include <string>
#include <vector>

using namespace std;

int main(int argc, char* argv[]) {
    if (argc < 4) return 1;

    string d = argv[1];
    string D = argv[2];
    string B = argv[3];

    ifstream file("DataBase.json");
    string line;
    bool found = false;

    while (getline(file, line)) {
        // یک جستجوی ساده برای پیدا کردن ردیفی که هر سه فاکتور را دارد
        if (line.find("\"inner_diameter\": " + d) != string::npos &&
            line.find("\"outer_diameter\": " + D) != string::npos &&
            line.find("\"width\": " + B) != string::npos) {
            
            // استخراج مدل از بین کوتیشن‌ها
            size_t first = line.find("\"model\": \"") + 10;
            size_t last = line.find("\"", first);
            cout << line.substr(first, last - first);
            found = true;
            break;
        }
    }

    if (!found) cout << "Not Found";
    return 0;
}
