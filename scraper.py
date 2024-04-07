import csv
import re
import requests

basic_fields = [
    "id",
    "title",
    "sellerType",
    "lat",
    "long",
    "placeId",
    "viewCount",
    "description",
    "price",
    "currency",
    "type",
    "year",
    "odometer",
    "odometerUnit",
    "sleeps",
    "roof",
    "make",
    "model",
    "fuel",
    "fridge",
    "sink",
    "stove",
    "oven",
    "table",
    "microwave",
    "ac",
    "airbags",
    "solar",
    "inverter",
    "shower",
    "extraStorage",
    "backupCamera",
    "ceilingFan",
    "heater",
    "toilet",
    "generator",
    "towHitch",
    "tv",
    "waterTank",
    "levelingJacks",
    "bikeRack",
    "4wd",
    "userId",
    "createdAt",
    "updatedAt",
    "expiresAt",
    "isSold",
    "soldAt",
    "isHidden",
    "isFlagged",
    "featureExpiresAt",
    "featuredImageId",
    "isFeatured",
    "isPending",
    "videoUrl",
    "isSocialRepostingOk",
    "wheelchairAccessible",
    "isReviewed",
    "originallyCreatedAt",
    "seats",
    "messagingMode",
    "adminName1",
    "countryCode",
    "client",
    "displayPrice",
    "slug",
    "isExpired"
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
    "isSold",
    "description"
]

csv_fields = [
    "title",
    "make",
    "model",
    "price",
    "odometer",
    "place",
    "year",
    "fuel",
    "isSold",
    "link",
]

query_limit = 50

include_distance = True
location = (39.833, -98.585)
distance = 500  # miles
description_filter_regex = "promaster"

if include_distance:
    csv_fields.insert(-1, "distance")


def main():
    base_query_params = get_base_query_params(select_fields)
    data = get_all_pages(base_query_params)
    if description_filter_regex is not None:
        data = filter_by_description(data)

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
        elif field == "place":
            row[field] = entry["place"]["placeName"] + ", " + entry["place"]["adminName1"]
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

    if include_distance:
        query_params["$modify[0]"] = "maxDistance"
        query_params["$modify[1]"] = location[0]
        query_params["$modify[2]"] = location[1]
        query_params["$modify[3]"] = distance

    for index, field in enumerate(fields):
        # fields to include are written as $select[0]=currency"
        query_params[f"$select[{index}]"] = field

    # also get location details
    query_params["$eager"] = "[place(defaultSelects)]"

    query_params["$sort[isSold]"] = 1

    if include_distance:
        query_params["$sort[distance]"] = 1
    else:
        query_params["$sort[createdAt]"] = -1

    query_params["countryCode[$ilike]"] = "%US%"

    return query_params


def add_paging_to_base_params(query_params, limit, page):
    offset = limit * page
    query_params["$limit"] = limit
    query_params["$skip"] = offset

    return query_params


def filter_by_description(data):
    return [item for item in data if re.search(description_filter_regex, item["description"], re.IGNORECASE)]


if __name__ == "__main__":
    main()
