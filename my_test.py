# -*- coding:utf-8 -*-
import systran_translation_api
import os

api_key_file = r'api_key.txt'
systran_translation_api.configuration.load_api_key(api_key_file)
api_client = systran_translation_api.ApiClient()
translation_api = systran_translation_api.TranslationApi(api_client)

source = "en"
target = "ar"
text = "how are you"
input = [text]
result = translation_api.translation_text_translate_get(source= source, target = target, input = input)

print result.outputs[0].output
