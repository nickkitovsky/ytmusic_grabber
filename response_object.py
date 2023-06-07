from common_utils import extract_chain, fields_to_str


class ResponseObject:
    def __init__(self, raw_response: dict) -> None:
        self.raw_response = raw_response

    @classmethod
    def parse(cls, raw_response: dict):
        match raw_response:
            # Page cases
            case {"header": header, "contents": contents, **other_keys}:
                return Page(header=header, contents=contents, other_keys=other_keys)
            # FEmusic_moods_and_genres inner page case
            case {"header": header, "items": items}:
                return Page(header=header, items=items)
            case {"contents": contents, **other_keys}:
                return Page(contents=contents, other_keys=other_keys)
            # FEmusic_moods_and_genres inner page case
            case {"buttonText": button_text, "clickCommand": click_command}:
                return Page(button_text=button_text, click_command=click_command)
            # Playlist cases
            case {
                "title": title,
                "subtitle": subtitle,
                "navigationEndpoint": navigation_endpoint,
            }:
                return Playlist(
                    title=title,
                    subtitle=subtitle,
                    navigation_endpoint=navigation_endpoint,
                )


class Page:
    def __init__(self, **kwargs):
        self.title = None
        self.subtitle = None
        self.items = None
        self.endpoint = None
        self.endpoint = self._parse_endpoint(kwargs)

        match kwargs:
            # FEmusic_home inner page case
            case {"header": header, "contents": list(contents)}:
                self.title = extract_chain(header, ("title", "text"))
                self._raw_items = contents
                try:
                    browse_id = extract_chain(
                        header,
                        ("title", "navigationEndpoint", "browseEndpoint", "browseId"),
                    )
                    self.endpoint = {"browse_id": browse_id}
                # If not found endpoint
                except TypeError:
                    pass
            case {"header": header, "contents": contents}:
                title_list = extract_chain(header, ("title", "runs"))
                self.title = fields_to_str(title_list)  # type: ignore
                try:
                    self._raw_items = extract_chain(
                        contents, ("content", "contents", "items")
                    )
                # FEmusic_moods_and_genres case
                except TypeError:
                    self._raw_items = extract_chain(contents, ("content", "contents"))
            # FEmusic_moods_and_genres inner page case
            case {"header": header, "items": items}:
                self.title = extract_chain(header, ("title", "runs", "text"))
                self._raw_items = items

            # FEmusic_home and FEmusic_library_landing cases
            case {"contents": contents}:
                contents = extract_chain(contents)
                if isinstance(contents, dict):
                    self.title = contents.get("title")
                    self._raw_items = extract_chain(contents, ("content", "contents"))
                    # FEmusic_library_landing case
                    if len(self._raw_items) == 1:
                        self._raw_items = extract_chain(self._raw_items[0])[
                            "items"
                        ]  # type: ignore
            # FEmusic_moods_and_genres inner page case
            case {"button_text": button_text, "click_command": click_command}:
                self.title = fields_to_str(button_text["runs"])
                self._raw_items = []
                self.endpoint = {
                    k: v
                    for k, v in click_command["browseEndpoint"].items()
                    # if k in self._endpoint_keys
                }

        self.items = [extract_chain(item) for item in self._raw_items]

    def _parse_endpoint(self, kwargs):
        if other_keys := kwargs.get("other_keys"):
            if response_context := other_keys.get("responseContext"):
                raw_endpoint = extract_chain(
                    response_context, ("serviceTrackingParams", 0, "params")
                )
                browse_id = [
                    r["value"] for r in raw_endpoint if r["key"] == 'browse_id'
                ][0]
                return {"browse_id": browse_id}
            # try:
            #     self.endpoint = {"browse_id": browse_id}
            # except IndexError:
            #     self.endpoint = None


class Playlist:
    def __init__(self, **kwargs) -> None:
        self.title = None
        self.subtitle = None
        self.items = None
        self.endpoint = None
        self._endpoint_keys = ("browseId", "params", "videoId", "playlistId")
        match kwargs:
            case {
                "title": title,
                "navigation_endpoint": navigation_endpoint,
                **other_keys,
            }:
                self.title = fields_to_str(title["runs"])
                if subtitle := other_keys.get("subtitle"):
                    self.subtitle = fields_to_str(subtitle["runs"])
                if browse_endpoint := navigation_endpoint.get("browseEndpoint"):
                    self.endpoint = {
                        k: v
                        for k, v in browse_endpoint.items()
                        if k in self._endpoint_keys
                    }
                elif watch_endpoint := navigation_endpoint.get("watchEndpoint"):
                    self.endpoint = {
                        k: v
                        for k, v in watch_endpoint.items()
                        if k in self._endpoint_keys
                    }


class Track:
    pass
