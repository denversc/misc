import hypothesis

disable_function_scoped_fixture_health_check = \
    hypothesis.settings(suppress_health_check=[hypothesis.HealthCheck.function_scoped_fixture])
