-- ════════════════════════════════════════════════════════════
-- Beat Cash — Supabase schema
-- À exécuter dans Supabase → SQL Editor → New query
-- ════════════════════════════════════════════════════════════

-- Profiles : 1 row par user (lié à auth.users de Supabase)
create table if not exists public.profiles (
  id            uuid primary key references auth.users(id) on delete cascade,
  email         text not null unique,
  display_name  text,
  plan          text not null default 'FREE',           -- FREE | PRO
  stripe_customer_id text,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

-- Subscriptions : suivi Stripe
create table if not exists public.subscriptions (
  id                       text primary key,             -- stripe sub id
  user_id                  uuid not null references public.profiles(id) on delete cascade,
  status                   text not null,                -- active | past_due | canceled | trialing
  price_id                 text not null,
  current_period_end       timestamptz not null,
  cancel_at_period_end     boolean not null default false,
  created_at               timestamptz not null default now(),
  updated_at               timestamptz not null default now()
);
create index if not exists subscriptions_user_idx on public.subscriptions(user_id);

-- Licenses : clés que le desktop utilise pour s'authentifier
create table if not exists public.licenses (
  key           text primary key,                         -- format: BC-XXXX-XXXX-XXXX-XXXX
  user_id       uuid not null references public.profiles(id) on delete cascade,
  plan          text not null default 'FREE',
  device_id     text,                                     -- optional binding (1 device par license)
  last_check    timestamptz,
  created_at    timestamptz not null default now()
);
create index if not exists licenses_user_idx on public.licenses(user_id);

-- Email subscribers (landing page capture)
create table if not exists public.email_subscribers (
  email         text primary key,
  source        text,                                     -- "free_pack" | "newsletter" | etc.
  free_pack_sent_at timestamptz,
  created_at    timestamptz not null default now()
);

-- ── RLS ─────────────────────────────────────────────────────
alter table public.profiles enable row level security;
alter table public.subscriptions enable row level security;
alter table public.licenses enable row level security;

create policy "users read own profile"
  on public.profiles for select
  using ( auth.uid() = id );

create policy "users update own profile"
  on public.profiles for update
  using ( auth.uid() = id );

create policy "users read own subs"
  on public.subscriptions for select
  using ( auth.uid() = user_id );

create policy "users read own licenses"
  on public.licenses for select
  using ( auth.uid() = user_id );

-- (les writes sur subscriptions/licenses passent par service_role depuis le webhook)

-- ── Trigger : création auto du profile quand auth.users insert ─────
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, email, display_name)
  values (new.id, new.email, coalesce(new.raw_user_meta_data->>'name', split_part(new.email, '@', 1)));
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();
