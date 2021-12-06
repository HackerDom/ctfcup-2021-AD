#include <iostream>
#include <fstream>
#include <vector>
#include <unordered_set>
#include <regex>


class FileWriter {
public:
    explicit FileWriter(const std::string& filename)
            : file(filename, std::ios::out | std::ios::binary)
    {
    }
    ~FileWriter() {
        file.close();
    }

    template<typename T>
    void write_value(T obj) {
        file.write((char*)&obj, sizeof(T));
    }

    template<typename T>
    void write_vector(std::vector<T> &obj) {
        file.write((char*)obj.data(), obj.size() * sizeof(T));
    }

    std::ofstream file;
};


class FileReader {
public:
    explicit FileReader(const std::string& filename)
            : file(filename, std::ios::in | std::ios::binary)
    {
    }
    ~FileReader() {
        file.close();
    }

    template<typename T>
    void read_value(T &obj) {
        file.read((char*)&obj, sizeof(T));
    }

    template<typename T>
    void read_vector(std::vector<T> &obj) {
        file.read((char*)obj.data(), obj.size() * sizeof(T));
    }

    std::ifstream file;
};



struct Trigger {
    unsigned int group;
    bool includes;
};


enum Action {
    DENY = false,
    ALLOW = true,
};


struct Rule {
    Trigger trigger;
    Action action;
};


struct Schema {
    std::vector<Rule> rules;
    std::vector<std::vector<unsigned int>> groups;
};


void dump(const std::string& filename, Schema& schema) {
    FileWriter file(filename);

    auto rules_size = schema.rules.size();
    file.write_value(rules_size);
    file.write_vector(schema.rules);

    auto groups_size = schema.groups.size();
    file.write_value(groups_size);
    for (int i = 0; i < groups_size; ++i) {
        auto group_size = schema.groups[i].size();
        file.write_value(group_size);
        file.write_vector(schema.groups[i]);
    }
}


void load(const std::string& filename, Schema& schema) {
    FileReader file(filename);

    unsigned long rules_size;
    file.read_value(rules_size);
    schema.rules.resize(rules_size);
    file.read_vector(schema.rules);

    unsigned long groups_size;
    file.read_value(groups_size);
    schema.groups.resize(groups_size);
    for (int i = 0; i < groups_size; ++i) {
        unsigned long group_size;
        file.read_value(group_size);
        schema.groups[i].resize(group_size);
        file.read_vector(schema.groups[i]);
    }
}


void print_schema(Schema &schema) {
    std::cout << "rules: " << std::endl;
    for (auto& rule: schema.rules) {
        std::cout << rule.trigger.group << " " << rule.trigger.includes << " " << rule.action << std::endl;
    }
    std::cout << "groups: " << std::endl;
    for (auto& group: schema.groups) {
        for (auto el: group) {
            std::cout << el << " ";
        }
        std::cout << std::endl;
    }
}


bool check(Schema& schema, unsigned int user) {
    print_schema(schema);

    std::unordered_set<unsigned int> user_groups(schema.groups[user].begin(), schema.groups[user].end());

    for (auto& rule: schema.rules) {
        if (rule.trigger.includes == (user_groups.find(rule.trigger.group) != user_groups.end())) {
            return rule.action == Action::ALLOW;
        }
    }

    return false;
}


char get_char_type(char c) {
    if (isspace(c)) {
        return 0;
    } else if (isalpha(c)) {
        return 1;
    } else if (c == '"') {
        return 2;
    } else if (ispunct(c)) {
        return 3;
    } else {
        return 4;
    }
}


template <typename T>
void split(std::string_view text, T consume) {
    if (text.empty()) {
        return;
    } else if (text.size() == 1) {
        if (!isspace(text[0])) {
            consume(text.substr(0, 1));
        }
        return;
    }
    int last_index = 0;
    char last_is_w = get_char_type(text[last_index]);
    for (int i = 1; i < text.size(); ++i) {
std::cout << "Compare '" << text[last_index] << "' and '" << text[i] << "'" << std::endl;
        if (last_is_w != get_char_type(text[i])) {
std::cout << "set: " << i << " " << text[last_index] << std::endl;
            if (!isspace(text[last_index])) {
                consume(text.substr(last_index, i - last_index));
            }
            last_index = i;
            last_is_w = get_char_type(text[i]);
        }
    }
    if (!isspace(text[last_index])) {
        consume(text.substr(last_index, text.size() - last_index));
    }
}


template<typename T>
struct Buffer {
    unsigned int size = 0;
    T data[3] = {};

    void add(T element) {
        data[size] = element;
        size++;
    }

    void clear() {
        size = 0;
    }
};


using UIntBuffer = Buffer<unsigned>;


struct ParseState {
    bool collect_rules = false;
    bool collect_groups = false;

    UIntBuffer buffer;
};


bool is_end(std::string_view part) {
    return part == "]]," || part == "]]}";
}


void consume_rule_part(Schema& schema, ParseState& state, std::string_view part) {
    if (part != ":[[" && part != "," && part != "],[" && part != "\"" && !is_end(part)) {
        std::cout << "Add num: " << part << std::endl;
        if (state.buffer.size == 3) {
            exit(1);
        }
        state.buffer.add(std::stoul(part.data()));

    } else if (part == "],[" || is_end(part)) {
std::cout << "flush rules: " << state.buffer.size << std::endl;
        if (state.buffer.size != 3) {
            exit(1);
        }

        schema.rules.push_back({
                                       {
                                               state.buffer.data[0],
                                               (bool) state.buffer.data[1],
                                       },
                                       (Action) state.buffer.data[2]
                               });
        state.buffer.clear();
        if (is_end(part)) {
            state.collect_rules = false;
        }
    }
}


void consume_group_part(Schema& schema, ParseState& state, std::string_view part) {
std::cout << "!" << part << "!" << std::endl;
    if (part != ":[[" && part != ":[[],[" && part != "," && part != "],[" && part != "\"" && !is_end(part)) {
        std::cout << "add part: " << part << " to index " << state.buffer.size << std::endl;
        auto int_part = std::stoul(part.data());
        std::cout << "parts_buffer_size: " << state.buffer.size << std::endl;
        state.buffer.add(int_part);
        std::cout << "parts_buffer_size: " << state.buffer.size << " -> " << state.buffer.size + 1 << std::endl;

        std::cout << "new part!: " << part << std::endl;
    } else if (part == "],[" || is_end(part)) {
std::cout << "flush parts, buffer size = " << state.buffer.size << std::endl;
        std::vector<unsigned int> group;
        group.reserve(state.buffer.size);

        for (int i = 0; i < state.buffer.size; ++i) {
std::cout << "add part: " << state.buffer.data[i] << std::endl;
            group.push_back(state.buffer.data[i]);
        }
        schema.groups.push_back(group);
        state.buffer.clear();
        std::cout << "new group!" << std::endl;
        if (is_end(part)) {
std::cout << "end of group collecting" << std::endl;
            state.collect_groups = false;
        }
    }
}


void consume_part(Schema& schema, ParseState& state, std::string_view part) {
    if (part == "rules") {
        if (state.collect_rules) {
            exit(1);
        }
            std::cout << "collect rules" << std::endl;
        state.buffer.clear();
        state.collect_rules = true;
    } else if (part == "groups") {
        if (state.collect_groups) {
            exit(1);
        }
            std::cout << "collect groups" << std::endl;
        state.buffer.clear();
        state.collect_groups = true;
    } else if (state.collect_rules) {
        consume_rule_part(schema, state, part);
    } else if (state.collect_groups) {
        consume_group_part(schema, state, part);
    }
}


Schema parse_schema(std::string_view text) {
    Schema schema;
    schema.groups.emplace_back();
    ParseState state;

    split(text, [&state, &schema](std::string_view part){consume_part(schema, state, part);});
    return schema;
}


int process_dump(char** argv) {
    std::string filename = argv[2];
    std::string raw_schema = argv[3];
    while (raw_schema.find("],[],[") != std::string::npos) {
        raw_schema = std::regex_replace(raw_schema, std::regex(R"(\],\[\],\[)"), "],[ ],[");
    }
    while (raw_schema.find("],[]]") != std::string::npos) {
        raw_schema = std::regex_replace(raw_schema, std::regex(R"(\],\[\]\])"), "],[ ]]");
    }
    std::cout << "after: " << raw_schema << std::endl;
    auto schema = parse_schema(raw_schema);
    dump(filename, schema);
    return 0;
}


int process_check(char** argv) {
    std::string filename = argv[2];
    unsigned int user = std::stoul(argv[3]);
    Schema schema;
    load(filename, schema);
    if (check(schema, user)) {
        return 0;
    }
    return 1;

}

int process_wrong_option() {
    return 1;
}


int main(int argc, char** argv) {
    if (argc < 4) {
        return process_wrong_option();
    }
    if (!strcmp(argv[1], "dump")) {
        return process_dump(argv);
    } else if (!strcmp(argv[1], "check")) {
        return process_check(argv);
    }
    return 0;
}
