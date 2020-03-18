"""Configurations for MLRun.

This file defines your configuration for MLRun. When running MLRun, pass a configuration name as the first argument.
"""
from typedconfig import Config, key, section, group_key


@section("logger")
class LoggerConfig(Config):
    name = key(cast=str)
    max_level = key(cast=str)


@section("camera")
class CameraConfig(Config):
    name = key(cast=str)
    id = key(cast=int)
    width = key(cast=int)
    height = key(cast=int)
    fps = key(cast=int)
    file = key(cast=str)


@section("engine")
class EngineConfig(Config):
    name = key(cast=str)
    path = key(cast=str)
    min_score = key(cast=float)
    width = key(cast=int)
    height = key(cast=int)


@section("publisher")
class PublisherConfig(Config):
    name = key(cast=str)
    team = key(cast=int)
    table = key(cast=str)
    prefix = key(cast=str)


class ConfigObject(Config):
    logger = group_key(LoggerConfig)
    camera = group_key(CameraConfig)
    engine = group_key(EngineConfig)
    publisher = group_key(PublisherConfig)
    show = key(cast=bool, section_name="debug")
