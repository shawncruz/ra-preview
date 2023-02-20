import datetime
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport


class RAService:
    def __init__(
        self,
    ):
        transport = RequestsHTTPTransport(
            url="https://ra.co/graphql",
            headers={
                "authority": "ra.co",
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9,es;q=0.8",
                "content-type": "application/json",
                "origin": "https://ra.co",
                "ra-content-language": "en",
                "referer": "https://ra.co/events/us/newyork",
                "sec-ch-device-memory": "8",
                "sec-ch-ua": '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
                "sec-ch-ua-arch": '"arm"',
                "sec-ch-ua-mobile": "?0",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            },
        )
        self.client = Client(transport=transport)

    def get_artists(
        self,
        start_date: datetime,
        end_date: datetime,
        area=8,
    ):
        query = gql(
            """
            query GET_EVENT_LISTINGS(
                $filters: FilterInputDtoInput
                $filterOptions: FilterOptionsInputDtoInput
                $page: Int
                $pageSize: Int
            ) {
                eventListings(
                    filters: $filters
                    filterOptions: $filterOptions
                    pageSize: $pageSize
                    page: $page
                ) {
                    data {
                        listingDate
                        event {
                            artists {
                                name
                            }
                        }
                    }
                    totalResults
                }
            }
        """
        )

        page = 1
        pageSize = 100
        maxPage = 10
        names = []
        while page < maxPage + 1:
            params = {
                "filters": {
                    "areas": {"eq": area},
                    "listingDate": {
                        "gte": start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "lte": end_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    },
                },
                "pageSize": pageSize,
                "page": page,
            }
            result = self.client.execute(query, variable_values=params)
            names.extend(
                [
                    artist["name"]
                    for data in result["eventListings"]["data"]
                    for artist in data["event"]["artists"]
                ]
            )
            if len(result["eventListings"]["data"]) < pageSize:
                break
            else:
                page += 1

        return names
