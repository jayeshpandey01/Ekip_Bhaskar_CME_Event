#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <iomanip>
#include <unordered_map>

// Generic data structure to hold row data
struct AceData {
    std::vector<std::string> values; // Store all column values as strings
    std::string datetime; // Formatted datetime (YYYYMMDDHHMM)
    std::string source_file;
};

// File configuration structure
struct FileConfig {
    std::string suffix;
    int skiprows;
    std::vector<std::string> columns;
    std::vector<std::string> na_values;
};

// Configuration for all ACE file types (mirrors Python's file_types)
std::unordered_map<std::string, FileConfig> file_types = {
    {"_ace_epam_5m", {
        "20250101_ace_epam_5m.txt",
        14,
        {"YR", "MO", "DA", "HHMM", "Julian Day", "Seconds of the Day",
         "Electron S", "38-53", "175-315", "Proton S", "47-68", "115-195",
         "310-580", "795-1193", "1060-1900", "Anis. Index"},
        {"-1.00e+05", "-1.00"}
    }},
    {"_ace_mag_1m", {
        "20250101_ace_mag_1m.txt",
        12,
        {"YR", "MO", "DA", "HHMM", "Julian Day", "Seconds of the Day",
         "S", "Bx", "By", "Bz", "Bt", "Lat.", "Long."},
        {"-999.9"}
    }},
    {"_ace_sis_5m", {
        "20250101_ace_sis_5m.txt",
        12,
        {"YR", "MO", "DA", "HHMM", "Julian Day", "Seconds of the Day",
         "S (>10 MeV)", ">10 MeV", "S (>30 MeV)", ">30 MeV"},
        {"-1.00e+05"}
    }},
    {"_ace_swepam_1m", {
        "20250101_ace_swepam_1m.txt",
        12,
        {"YR", "MO", "DA", "HHMM", "Julian Day", "Seconds of the Day",
         "S", "Proton Density", "Bulk Speed", "Ion Temperature"},
        {"-9999.9", "-1.00e+05"}
    }}
};

// Function to format datetime from YR, MO, DA, HHMM
std::string format_datetime(const std::string& yr, const std::string& mo,
                           const std::string& da, const std::string& hhmm) {
    std::stringstream ss;
    ss << yr << std::setw(2) << std::setfill('0') << mo
       << std::setw(2) << std::setfill('0') << da
       << std::setw(4) << std::setfill('0') << hhmm;
    return ss.str(); // Format: YYYYMMDDHHMM
}

// Function to check if a value is missing
bool is_missing(const std::string& value, const std::vector<std::string>& na_values) {
    for (const auto& na : na_values) {
        if (value == na) return true;
    }
    return false;
}

// Function to check if a file exists
bool file_exists(const std::string& file_path) {
    std::ifstream file(file_path.c_str());
    return file.good();
}

// Function to load an ACE file
std::vector<AceData> load_ace_file(const std::string& file_path, const FileConfig& config) {
    std::vector<AceData> data;
    std::ifstream file(file_path.c_str());
    if (!file.is_open()) {
        std::cerr << "Error: Could not open file " << file_path << std::endl;
        return data;
    }

    std::string line;
    // Skip header rows
    for (int i = 0; i < config.skiprows && std::getline(file, line); ++i) {
        std::cout << "Skipped header line " << i + 1 << ": " << line << std::endl;
    }

    // Read data lines
    int line_count = 0;
    while (std::getline(file, line)) {
        line_count++;
        std::istringstream iss(line);
        AceData row;
        row.values.resize(config.columns.size());
        std::string value;

        // Read all columns
        for (size_t i = 0; i < config.columns.size() && iss >> value; ++i) {
            row.values[i] = is_missing(value, config.na_values) ? "-9999.9" : value;
        }

        // Check if enough columns were read
        if (row.values.size() < 4) {
            std::cerr << "Warning: Line " << line_count << " in " << file_path
                      << " has fewer columns than expected (" << row.values.size() << "< 4)" << std::endl;
            continue;
        }

        // Create datetime from YR, MO, DA, HHMM
        row.datetime = format_datetime(row.values[0], row.values[1], row.values[2], row.values[3]);

        // Extract filename from path
        size_t last_slash = file_path.find_last_of("/\\");
        row.source_file = last_slash == std::string::npos ? file_path : file_path.substr(last_slash + 1);
        data.push_back(row);
    }

    file.close();
    std::cout << "Processed " << line_count << " data lines from " << file_path << std::endl;
    return data;
}

// Function to write data to CSV
void write_to_csv(const std::vector<AceData>& data, const std::string& output_path,
                  const std::vector<std::string>& columns) {
    std::ofstream file(output_path.c_str());
    if (!file.is_open()) {
        std::cerr << "Error: Could not open output file " << output_path << std::endl;
        return;
    }

    // Write header
    file << "datetime";
    for (const auto& col : columns) {
        file << "," << col;
    }
    file << ",source_file\n";

    // Write data
    for (const auto& row : data) {
        file << row.datetime;
        for (const auto& value : row.values) {
            file << "," << value;
        }
        file << "," << row.source_file << "\n";
    }

    file.close();
    std::cout << "CSV file written to " << output_path << std::endl;
}

// Function to process a single file
bool process_file(const std::string& file_path, const std::string& file_type,
                 const FileConfig& config, const std::string& base_output_path) {
    std::cout << "Processing file: " << file_path << std::endl;
    std::cout << "Expected suffix: " << config.suffix << std::endl;

    if (!file_exists(file_path)) {
        std::cerr << "Error: File not found - " << file_path << std::endl;
        return false;
    }

    // Check suffix (less strict due to C++11 limitations)
    if (file_path.find(config.suffix) == std::string::npos) {
        std::cerr << "Error: Incorrect suffix for " << file_path
                  << ". Expected " << config.suffix << std::endl;
        return false;
    }

    auto data = load_ace_file(file_path, config);
    if (data.empty()) {
        std::cerr << "No data loaded from " << file_path << std::endl;
        return false;
    }

    // Generate output CSV path
    std::string output_path = base_output_path + file_type + ".csv";
    write_to_csv(data, output_path, config.columns);
    return true;
}

int main() {
    // Base path for input and output
    std::string base_path = "C:/Users/harsh/Downloads/aditya-l1-isro-main/ace_daily/2025";
    std::string base_output_path = "C:/Users/harsh/Downloads/aditya-l1-isro-main/csv_file";

    // Check if directory exists by testing one file
    std::string test_file = base_path ;
    if (!file_exists(test_file)) {
        std::cerr << "Directory or files not found. Please check: " << base_path << std::endl;
        std::cerr << "Test file checked: " << test_file << std::endl;
        return 1;
    }

    // Process each file
    std::vector<std::pair<std::string, std::string>> file_paths = {
        {"_ace_epam_5m", base_path },
        {"_ace_mag_1m", base_path },
        {"_ace_sis_5m", base_path },
        {"_ace_swepam_1m", base_path}
    };

    int processed_files = 0;
    for (const auto& p : file_paths) {
        const std::string& file_type = p.first;
        const std::string& file_path = p.second;
        if (file_types.find(file_type) != file_types.end()) {
            if (process_file(file_path, file_type, file_types[file_type], base_output_path)) {
                processed_files++;
            }
        }
    }

    std::cout << "Processed " << processed_files << " files successfully." << std::endl;
    return 0;
}
