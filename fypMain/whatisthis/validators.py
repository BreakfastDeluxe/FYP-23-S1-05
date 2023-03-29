from django.core.exceptions import ValidationError


def validate_file_size(value):
    filesize= value.size
    #print('debug filesize: ')
    #print(filesize)
    if filesize > 10485760: #in bytes i.e. 1Mb
        raise ValidationError("You cannot upload file more than 1Mb")
    else:
        return value