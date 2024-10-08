from httptoolkit.sent_request_log_record import RequestLogRecord


def test_get_request_format(get_sent_request):
    assert (
        str(RequestLogRecord(get_sent_request)) == "Sending GET https://example.com:4321/put/some/data/here"
        "?please=True&carefully=True"
    )


def test_post_request_format(post_sent_request):
    assert (
        str(RequestLogRecord(post_sent_request)) == "Sending POST https://example.com:4321/put/some/data/here"
        "?please=True&carefully=True (body: 43)"
    )


def test_args(post_sent_request):
    assert RequestLogRecord(post_sent_request).args() == {
        "method": "POST",
        "url": "https://example.com:4321/put/some/data/here?please=True&carefully=True",
        "headers": "ServiceHeader: service-header\nRequestHeader: request-header",
        "body_size": 43,
    }


def test_args_json(x_sent_request_dict_json):
    metod, x_request = x_sent_request_dict_json
    assert RequestLogRecord(x_request).args() == {
        "method": metod,
        "url": "https://example.com:4321/put/some/data/here?please=True&carefully=True",
        "headers": "ServiceHeader: service-header\nRequestHeader: request-header\nContent-Type: application/json",
        "body_size": 29,
    }
