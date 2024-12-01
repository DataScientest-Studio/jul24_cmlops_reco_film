-- Activer RLS sur la table users
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Policy pour permettre à l'utilisateur authentifié de voir uniquement ses propres données
CREATE POLICY "Les utilisateurs peuvent voir leurs propres données"
ON public.users
FOR ALL
TO authenticated
USING ("authId" = auth.uid()::text);

-- Policy pour permettre à l'utilisateur anonyme de ne rien voir
CREATE POLICY "Les utilisateurs anonymes ne peuvent rien voir"
ON public.users
FOR ALL
TO anon
USING (false);

-- Policy pour permettre au rôle service_role de tout voir
CREATE POLICY "Le service_role peut tout voir"
ON public.users
FOR ALL
TO service_role
USING (true); 
