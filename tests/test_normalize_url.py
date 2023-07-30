from tinygen.hello import norm_repo_spec


def test_normalize_url():
    assert (
        norm_repo_spec("leoshimo/copier_python_template")
        == "leoshimo/copier_python_template"
    )
    assert (
        norm_repo_spec("https://github.com/leoshimo/copier_python_template")
        == "leoshimo/copier_python_template"
    )
    assert (
        norm_repo_spec(
            "https://github.com/leoshimo/copier_python_template?jibberish=hi"
        )
        == "leoshimo/copier_python_template"
    )
