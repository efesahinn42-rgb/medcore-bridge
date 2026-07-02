from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult


def _tc_kimlik_checksum_valid(digits: str) -> bool:
    d = [int(c) for c in digits]
    if d[0] == 0:
        return False
    odd_sum = d[0] + d[2] + d[4] + d[6] + d[8]
    even_sum = d[1] + d[3] + d[5] + d[7]
    check10 = ((odd_sum * 7) - even_sum) % 10
    if check10 != d[9]:
        return False
    check11 = sum(d[:10]) % 10
    return check11 == d[10]


class TrIdNumberRecognizer(PatternRecognizer):
    """TC Kimlik No — checksum ile doğrulanır, sahte 11 haneli sayıları eler."""

    PATTERNS = [Pattern(name="tc_kimlik", regex=r"\b\d{11}\b", score=0.4)]
    CONTEXT = ["tc", "tc kimlik", "kimlik no", "kimlik numarası", "t.c."]

    def __init__(self) -> None:
        super().__init__(
            supported_entity="TR_ID_NUMBER",
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language="en",
        )

    def validate_result(self, pattern_text: str) -> bool | None:
        digits = "".join(ch for ch in pattern_text if ch.isdigit())
        if len(digits) != 11:
            return False
        return _tc_kimlik_checksum_valid(digits)


class PassportNumberRecognizer(PatternRecognizer):
    """Pasaport no — ülkeler arası format farklılığı nedeniyle yaklaşık bir desen.

    Kesin doğrulama yok; bağlam kelimeleriyle (pasaport/passport) güven skoru artırılıyor.
    """

    PATTERNS = [Pattern(name="passport", regex=r"\b[A-Z]{1,2}[0-9]{6,9}\b", score=0.3)]
    CONTEXT = ["pasaport", "passport", "passport no", "passport number"]

    def __init__(self) -> None:
        super().__init__(
            supported_entity="PASSPORT",
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language="en",
        )


def get_custom_recognizers() -> list[PatternRecognizer]:
    return [TrIdNumberRecognizer(), PassportNumberRecognizer()]


__all__ = ["get_custom_recognizers", "RecognizerResult"]
