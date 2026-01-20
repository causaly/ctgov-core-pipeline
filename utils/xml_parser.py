class XMLParser:
    def __init__(self, rules):
        self.rules = rules["rules"]
        self.default_value = '0'

    def sanitize_str(self, input_str):
        if input_str:
            input_str = " ".join(input_str.replace('\n', ' ').replace('\t', ' ').strip().split())

        else:
            return self.default_value
        return input_str

    def start_parsing(self, xml):
        output = self.extract_fields(xml, self.rules)
        return output

    def extract_fields(self, root, rules):
        extracted_obj = {}
        for each_rule in rules:
            if "xpath" in each_rule:
                elements = root.findall(each_rule["xpath"])
                if "plural" in each_rule:
                    obj_list = []
                    for child_el in elements:
                        obj_list.append(self.extract_fields(child_el, each_rule["rules"]))
                    if each_rule["field"] in extracted_obj:
                        extracted_obj[each_rule["field"]].extend(obj_list)
                    else:
                        extracted_obj[each_rule["field"]] = obj_list
                else:
                    value = self.default_value
                    if len(elements) == 1:
                        if "no_sanitize" in each_rule:
                            value = ' '.join(elements[0].itertext())
                        else:
                            if "no_sanitize" in each_rule:
                                value = ' '.join(elements[0].itertext())
                            else:
                                value = self.sanitize_str(' '.join(elements[0].itertext()))
                    elif len(elements) > 1:
                        value = [self.sanitize_str(' '.join(elem.itertext())) for elem in elements]

                    extracted_obj[each_rule["field"]] = value
        return extracted_obj

