from vuln import convert_cpe, keyword_search


def test_convert_cpe_basic():
    result = convert_cpe("cpe:/a:vsftpd:vsftpd:2.3.4")
    assert result == "cpe:2.3:a:vsftpd:vsftpd:2.3.4:*:*:*:*:*:*:*"


def test_convert_cpe_noversion():
    result = convert_cpe("cpe:/a:mysql:mysql")
    assert result == "cpe:2.3:a:mysql:mysql:*:*:*:*:*:*:*"


def test_keyword_search_with_version():
    result = keyword_search("cpe:2.3:a:vsftpd:vsftpd:2.3.4:*:*:*:*:*:*:*")
    assert result == "vsftpd vsftpd"


def test_keyword_no_version():
    result = keyword_search("cpe:2.3:a:mysql:mysql:*:*:*:*:*:*:*")
    assert result == ""
