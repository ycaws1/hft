from app.data.provider import DataProvider


class DataProviderRegistry:
    def __init__(self):
        self._providers: dict[str, DataProvider] = {}
        self._default: str | None = None

    def register(self, provider: DataProvider, default: bool = False) -> None:
        self._providers[provider.name] = provider
        if default or self._default is None:
            self._default = provider.name

    def get(self, name: str | None = None) -> DataProvider:
        key = name or self._default
        if key is None or key not in self._providers:
            raise ValueError(
                f"Data provider '{key}' not found. Available: {list(self._providers.keys())}"
            )
        return self._providers[key]

    @property
    def available(self) -> list[str]:
        return list(self._providers.keys())


registry = DataProviderRegistry()
