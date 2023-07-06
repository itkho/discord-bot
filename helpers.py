def get_message_id_from_link(link: str) -> int:
    return int(link.split("/")[-1])
