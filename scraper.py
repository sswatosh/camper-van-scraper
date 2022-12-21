import csv
import requests

all_fields = [
    "id",
    "title",
    "price",
    "odometer",
    "odometerUnit",
    "seats",
    "sleeps",
    "year",
    "fuel",
    "currency",
    "isSold",
    "isPending",
    "createdAt",
    "videoUrl",
    "messagingMode",
    "make",
    "model"
]

select_fields = [
    "id",
    "title",
    "price",
    "odometer",
    "year",
    "fuel",
    "make",
    "model",
    "isSold"
]

csv_fields = [
    "title",
    "make",
    "model",
    "price",
    "odometer",
    "year",
    "fuel",
    "isSold",
    "link",
]

query_limit = 50


def main():
    base_query_params = get_base_query_params(select_fields)
    data = get_all_pages(base_query_params)

    with open("vans.csv", "w", encoding="UTF-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_fields)
        writer.writeheader()
        for entry in data:
            row = get_csv_row_from_entry(entry)
            writer.writerow(row)


def get_csv_row_from_entry(entry):
    row = {}
    for field in csv_fields:
        if field == "link":
            row[field] = "https://thevancamper.com/post/" + str(entry["id"])
        elif field == "price":
            row[field] = entry[field] / 100
        else:
            row[field] = entry[field]
    return row


def get_all_pages(base_params):
    data = []
    current_page = 0
    new_page_data = get_page(base_params, current_page)
    while len(new_page_data) > 0:
        data.extend(new_page_data)
        current_page += 1
        new_page_data = get_page(base_params, current_page)

    return data


def get_page(base_params, page):
    full_params = add_paging_to_base_params(base_params, query_limit, page)

    param_strings = [f"{name}={str(value)}" for name, value in full_params.items()]
    query_string = "&".join(param_strings)

    response = requests.get("https://api.thevancamper.com/posts", params=query_string)

    return response.json()["data"]


def get_base_query_params(fields):
    query_params = {}
    for index, field in enumerate(fields):
        # fields to include are written as $select[0]=currency"
        query_params[f"$select[{index}]"] = field

    query_params["$sort[isSold]"] = 1
    query_params["$sort[createdAt]"] = -1
    query_params["countryCode[$ilike]"] = "%US%"

    return query_params


def add_paging_to_base_params(query_params, limit, page):
    offset = limit * page
    query_params["$limit"] = limit
    query_params["$skip"] = offset

    return query_params


if __name__ == "__main__":
    main()
