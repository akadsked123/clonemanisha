from django.shortcuts import redirect

ALLOWED_ITEMS_PER_PAGE = [25, 50, 100, 250, 500]

def validate_items_per_page(items_per_page=None, request=None, page_number=1, group_id=None):
    if items_per_page is None:
        items_per_page = 25
    if request is None:
        return items_per_page

    try:
        items_per_page = int(items_per_page)
        if items_per_page not in ALLOWED_ITEMS_PER_PAGE:
            if group_id:
                return redirect(f"{request.path}?group={group_id}&page={page_number}&items_per_page=25")
            else:
                return redirect(f"{request.path}?page={page_number}&items_per_page=25")
    except ValueError:
        if group_id:
            return redirect(f"{request.path}?group={group_id}&page={page_number}&items_per_page=25")
        else:
            return redirect(f"{request.path}?page={page_number}&items_per_page=25")
    
    return items_per_page