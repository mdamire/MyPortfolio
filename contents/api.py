from basehome.models import Files

def get_file_from_key(key):
    try: 
        return Files.objects.get(key=key)
    except Files.DoesNotExist:
        return None
