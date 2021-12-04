#include <iostream>
#include <fstream>
#include <vector>
#include <unordered_set>

using namespace std;


int set_bit(int value, int bit) {
    return value | (1 << bit);
}


int clear_bit(int value, int bit) {
    return value & ~(1 << bit);
}


int get_code(const vector<unsigned int>& groups) {
    int res = 0;
    for (auto group: groups) {
        res = set_bit(res, group);
    }
    return res;
}



class FileWriter {
public:
    explicit FileWriter(const string& filename)
            : file(filename, ios::out | ios::binary)
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
    void write_vector(vector<T> &obj) {
        file.write((char*)obj.data(), obj.size() * sizeof(T));
    }

    ofstream file;
};


class FileReader {
public:
    explicit FileReader(const string& filename)
            : file(filename, ios::in | ios::binary)
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
    void read_vector(vector<T> &obj) {
        file.read((char*)obj.data(), obj.size() * sizeof(T));
    }

    ifstream file;
};



struct Trigger {
    unsigned int user;
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
    vector<Rule> rules;
    vector<vector<unsigned int>> groups;
};


void dump(const string& filename, Schema& schema) {
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


void load(const string& filename, Schema& schema) {
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
    cout << "rules: " << endl;
    for (auto& rule: schema.rules) {
        cout << rule.trigger.user << " " << rule.trigger.group << " " << rule.trigger.includes << " " << rule.action << endl;
    }
    cout << "groups: " << endl;
    for (auto& group: schema.groups) {
        for (auto el: group) {
            cout << el << " ";
        }
        cout << endl;
    }
}


bool check(Schema& schema, unsigned int user) {
    unordered_set<int> user_groups(schema.groups[user].begin(), schema.groups[user].end());

    for (auto& rule: schema.rules) {
        if (rule.trigger.user == user) {
            if (rule.trigger.includes == (user_groups.find(rule.trigger.group) != user_groups.end())) {
                return rule.action == Action::ALLOW;
            }
        }
    }

    return false;
}


static int print_cnt = 0;


void p() {
    cout << "debug print " << print_cnt++ << endl;
}


Schema get_schema() {
    return Schema({
                          {
                                  Rule({Trigger({12, 54, true}), Action::DENY}),
                                  Rule({Trigger({34, 43, false}), Action::ALLOW}),
                                  Rule({Trigger({56, 32, true}), Action::DENY}),
                                  Rule({Trigger({78, 21, true}), Action::DENY}),
                          },
                          {
                                  {0, 1, 2},
                                  {0},
                                  {0, 1, 2},
                                  {1, 2},
                                  {1, 2},
                                  {1},
                                  {0, 1},
                                  {1},
                                  {1},
                                  {1},
                                  {1},
                          }
                  });
}


void _find_rules() {

}


char get_char_type(char c) {
    if (isspace(c)) {
        return 0;
    } else if (isalpha(c)) {
        return 1;
    } else if (ispunct(c)) {
        return 2;
    } else {
        return 5;
    }
}


template <typename T>
void split(string_view text, T consume) {
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
//        cout << "Compare '" << text[last_index] << "' and '" << text[i] << "'" << endl;
        if (last_is_w != get_char_type(text[i])) {
//            cout << "set: " << i << " " << text[last_index] << endl;
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


struct ParseState {
    bool collect_rules = false;
    bool collect_groups = false;

    unsigned int parts_buffer[4] = {};
    unsigned int parts_buffer_size = 0;
};


bool is_end(string_view part) {
    return part == "]],\"" || part == "]]}";
}


void consume_rule_part(Schema& schema, ParseState& state, string_view part) {
    if (part != "\":[[" && part != "," && part != "],[" && !is_end(part)) {
//        cout << "Add num: " << part << endl;
        if (state.parts_buffer_size == 4) {
            throw invalid_argument("Invalid rules array size");
        }
        state.parts_buffer[state.parts_buffer_size++] = stoul(part.data());
    } else if (part == "],[" || is_end(part)) {
//        cout << "flush rules: " << state.parts_buffer_size << endl;
        if (state.parts_buffer_size != 4) {
            throw invalid_argument("Invalid rules array size at the end");
        }

        schema.rules.push_back({
                                       {
                                               state.parts_buffer[0],
                                               state.parts_buffer[1],
                                               (bool) state.parts_buffer[2],
                                       },
                                       (Action) state.parts_buffer[3]
                               });
        state.parts_buffer_size = 0;
        if (is_end(part)) {
            state.collect_rules = false;
        }
    }
}


void consume_group_part(Schema& schema, ParseState& state, string_view part) {
//    cout << "!" << part << "!" << endl;
    if (part != "\":[[" && part != "," && part != "],[" && !is_end(part)) {
//        cout << "part: " << part << " !" << endl;
        state.parts_buffer[state.parts_buffer_size++] = stoul(part.data());

//        cout << "new part!: " << part << endl;
    } else if (part == "],[" || is_end(part)) {
//        cout << "flush parts, buffer size = " << state.parts_buffer_size << endl;
//        vector<unsigned int> group(state.parts_buffer, state.parts_buffer + state.parts_buffer_size);
        vector<unsigned int> group;
        group.reserve(state.parts_buffer_size);

        for (int i = 0; i < state.parts_buffer_size; ++i) {
//            cout << "add part: " << state.parts_buffer[i] << endl;
            group.push_back(state.parts_buffer[i]);
        }
        schema.groups.push_back(group);
        state.parts_buffer_size = 0;
//        cout << "new group!" << endl;
        if (is_end(part)) {
//            cout << "end of group collecting" << endl;
            state.collect_groups = false;
        }
    }
}


void consume_part(Schema& schema, ParseState& state, string_view part) {
    if (part == "rules") {
        if (state.collect_rules) {
            throw invalid_argument("Duplicated rules");
        }
//            cout << "collect rules" << endl;
        state.parts_buffer_size = 0;
        state.collect_rules = true;
    } else if (part == "groups") {
        if (state.collect_groups) {
            throw invalid_argument("Duplicated groups");
        }
//            cout << "collect groups" << endl;
        state.parts_buffer_size = 0;
        state.collect_groups = true;
    } else if (state.collect_rules) {
        consume_rule_part(schema, state, part);
    } else if (state.collect_groups) {
        consume_group_part(schema, state, part);
    }
}


Schema parse_schema(string_view text) {
    Schema schema;
    ParseState state;

    split(text, [&state, &schema](string_view part){consume_part(schema, state, part);});
    return schema;
}


extern "C" int add_func(int a, int b) {
    return a + b;
}



//extern "C" void check_schema(char* path, unsigned int user) {
//    auto schema = parse_schema(raw_schema);
//    check(schema, user);
//}
