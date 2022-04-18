class MetricComputation:
    @staticmethod
    def get_sum_across_page(account_metrics_mapping):
        output = []
        for row in list(account_metrics_mapping.values()):
            if type(row) != list:
                row = [row]
            for r in row:

                value = r["value"]
                slug = r["slug"]
                name = r["name"]
                date = r["date"]

                if not value:
                    if  value != 0:
                        continue

                if type(value) == dict:
                    sum(value.values())

                found = False
                for index, item in enumerate(output):
                    if item["slug"] == slug and item["date"] == date and type(value) == dict :
                        for k1, v1 in item["value"].items():
                            output[index]["value"][k1] += value.get(k1, 0)
                        found = True
                if not found:
                    output.append(
                        {"value": value if type(value) == dict else int(value), "slug": slug, "name": name, "date": date}
                    )
        return output
