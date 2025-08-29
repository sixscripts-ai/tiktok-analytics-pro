from .unified_analyzer import UnifiedTikTokAnalyzer


def main() -> None:
    analyzer = UnifiedTikTokAnalyzer(depth="deep")
    url = "https://www.tiktok.com/@2wpeezy4"
    report = analyzer.analyze(url)
    print(report)


if __name__ == "__main__":
    main()
