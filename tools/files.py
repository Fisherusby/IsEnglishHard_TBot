import uuid
import os
import requests
from tools.translate import get_user_dictionary


def dict_to_file(user_id):
    dictionary = get_user_dictionary(user_id)
    unique_filename = f'./tmp/{user_id}/dictionary.txt'
    os.makedirs(os.path.dirname(unique_filename), exist_ok=True)

    with open(unique_filename, 'w', encoding='utf-8') as handle:
        handle.writelines('\n'.join(sorted(dictionary)))

    return unique_filename


def download_photo(url):
    unique_filename = str(uuid.uuid4())
    file_name = f'./downloads/photos/{unique_filename}.{url.split("/")[-1].split(".")[-1]}'
    file_exists = os.path.exists(file_name)
    print(f'{file_name = }')
    if file_exists:
        print(f'file {file_name} is exist')
        return

    with open(file_name, 'wb') as handle:
        response = requests.get(url)

        if not response.ok:
            print(response)

        for block in response.iter_content(1024):
            if not block:
                break
            handle.write(block)