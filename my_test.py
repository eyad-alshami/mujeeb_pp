# -*- coding:utf-8 -*-
import systran_translation_api
import os



if __name__=="__main__":
	api_key_file = r'api_key.txt'
	systran_translation_api.configuration.load_api_key(api_key_file)
	api_client = systran_translation_api.ApiClient()
	translation_api = systran_translation_api.TranslationApi(api_client)

	source = "ar"
	target = "en"
	text = "أنا أتكلم معك"
	input = [text]
	result = translation_api.translation_text_translate_get(source= source, target = target, input = input)

	print unicode(result.outputs[0].output, "utf-8")