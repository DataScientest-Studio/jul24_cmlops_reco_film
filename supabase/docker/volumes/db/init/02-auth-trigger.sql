CREATE OR REPLACE FUNCTION public.handle_new_user() 
RETURNS trigger AS $$
DECLARE
    user_id integer;
    email_local text;
    numbers text;
BEGIN
    -- Extraire la partie locale de l'email (avant @)
    email_local := split_part(NEW.email, '@', 1);
    
    -- Extraire tous les chiffres de la partie locale
    numbers := regexp_replace(email_local, '[^0-9]', '', 'g');
    
    -- Tenter de convertir en nombre
    BEGIN
        IF numbers <> '' THEN
            user_id := numbers::integer;
            
            -- Mettre à jour la table users avec l'ID auth
            UPDATE public.users 
            SET "authId" = NEW.id::text
            WHERE "userId" = user_id;
        END IF;
        
    EXCEPTION WHEN others THEN
        -- Si la conversion échoue, on ignore silencieusement
        RAISE NOTICE 'Could not extract valid user_id from email: %', email_local;
    END;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Créer le trigger sur la table auth.users
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();
