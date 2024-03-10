import httpx

class HTTPClientConfig:
    # Maintain a global configuration dictionary
    _global_config = {
        "timeout": 120.0,
        "follow_redirects": True,
        "headers": {},
    }

    @staticmethod
    def set_option(option, value):
        """
        Set a global configuration option for the HTTP client.

        :param option: Configuration option to set.
        :param value: Value to assign to the option.
        """
        if option in HTTPClientConfig._global_config:
            HTTPClientConfig._global_config[option] = value
        else:
            raise ValueError(f"Unknown configuration option: {option}")

    @staticmethod
    def get_option(option):
        """
        Get the current value of a configuration option.

        :param option: Configuration option to retrieve.
        :return: The value of the specified configuration option.
        """
        return HTTPClientConfig._global_config.get(option, None)

    @staticmethod
    def create_client() -> httpx.Client:
        """
        Creates a new httpx.Client instance using the current global configuration.

        :return: An httpx.Client instance.
        """
        return httpx.Client(
            timeout=HTTPClientConfig._global_config["timeout"],
            follow_redirects=HTTPClientConfig._global_config["follow_redirects"],
            headers=HTTPClientConfig._global_config["headers"]
        )

    @staticmethod
    def create_async_client() -> httpx.AsyncClient:
        """
        Creates a new httpx.AsyncClient instance using the current global configuration.

        :return: An httpx.AsyncClient instance.
        """
        return httpx.AsyncClient(
            timeout=HTTPClientConfig._global_config["timeout"],
            follow_redirects=HTTPClientConfig._global_config["follow_redirects"],
            headers=HTTPClientConfig._global_config["headers"]
        )