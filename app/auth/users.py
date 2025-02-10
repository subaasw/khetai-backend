from app.database import supabase

def google_login():
    response = supabase.auth.sign_in_with_oauth({   
        "provider": 'google'
    })
    return response
