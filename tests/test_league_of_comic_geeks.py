from dex_starr.service.league_of_comic_geeks.session import Session as LeagueOfComicGeeks


def test_comic_list(league_of_comic_geeks: LeagueOfComicGeeks):
    results = league_of_comic_geeks.comic_list(
        search_term="Tales from the Dark Multiverse: Batman - Knightfall #1"
    )
    assert results is not None


def test_series(league_of_comic_geeks: LeagueOfComicGeeks):
    result = league_of_comic_geeks.series(id_=156046)
    assert result is not None


def test_comic(league_of_comic_geeks: LeagueOfComicGeeks):
    result = league_of_comic_geeks.comic(id_=5327798)
    assert result is not None
