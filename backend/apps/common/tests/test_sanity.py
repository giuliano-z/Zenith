"""Test de sanity de Fase 1: verifica que el entorno de test y Django arrancan."""
from django.conf import settings


def test_settings_loaded():
    assert settings.configured


def test_python_truth():
    assert 1 + 1 == 2
