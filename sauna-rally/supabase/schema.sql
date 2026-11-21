-- サウナスタンプラリー：サーバー側の押印判定（Supabase / PostgreSQL）
-- 端末から送られた位置をサーバーで判定し、合格したときだけスタンプを記録する。
-- ルールは index.html の judge() と同じ。値を変えるときは両方そろえる。

create table if not exists public.facilities (
  id        text primary key,
  name      text not null,
  short     text not null,
  region    text not null,
  lat       double precision not null,
  lng       double precision not null,
  radius_m  integer not null default 150,
  active    boolean not null default true
);

create table if not exists public.stamps (
  id          bigint generated always as identity primary key,
  user_id     uuid not null references auth.users(id) on delete cascade,
  facility_id text not null references public.facilities(id),
  stamped_at  timestamptz not null default now(),
  stamp_date  date not null default (now() at time zone 'Asia/Tokyo')::date,
  lat         double precision not null,
  lng         double precision not null,
  accuracy_m  double precision not null,
  distance_m  double precision not null,
  unique (user_id, facility_id, stamp_date)
);

-- 不合格も含めた試行ログ（不正の傾向を後から見るため）
create table if not exists public.checkin_attempts (
  id          bigint generated always as identity primary key,
  user_id     uuid,
  facility_id text,
  at          timestamptz not null default now(),
  lat         double precision,
  lng         double precision,
  accuracy_m  double precision,
  distance_m  double precision,
  result      text not null
);

alter table public.facilities       enable row level security;
alter table public.stamps           enable row level security;
alter table public.checkin_attempts enable row level security;

drop policy if exists "facilities readable" on public.facilities;
create policy "facilities readable" on public.facilities for select using (true);
drop policy if exists "own stamps readable" on public.stamps;
create policy "own stamps readable" on public.stamps for select using (auth.uid() = user_id);
-- stamps / checkin_attempts への insert は stamp_checkin() 経由のみ（ポリシーを作らない）

create or replace function public.distance_m(lat1 double precision, lng1 double precision, lat2 double precision, lng2 double precision)
returns double precision language sql immutable as $$
  select 2 * 6371008.8 * asin(least(1, sqrt(
    power(sin(radians(lat2 - lat1) / 2), 2) +
    cos(radians(lat1)) * cos(radians(lat2)) * power(sin(radians(lng2 - lng1) / 2), 2)
  )))
$$;

create or replace function public.stamp_checkin(p_facility text, p_lat double precision, p_lng double precision, p_accuracy double precision)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  c_max_accuracy  constant double precision := 150;
  c_grace         constant double precision := 50;
  c_daily_limit   constant integer := 10;
  c_max_speed_kmh constant double precision := 250;
  v_uid   uuid := auth.uid();
  v_f     facilities%rowtype;
  v_d     double precision;
  v_today date := (now() at time zone 'Asia/Tokyo')::date;
  v_last  stamps%rowtype;
  v_km    double precision;
  v_h     double precision;
  v_res   text;
begin
  if v_uid is null then
    return jsonb_build_object('ok', false, 'code', 'not_signed_in');
  end if;

  select * into v_f from facilities where id = p_facility and active;
  if not found then
    v_res := 'unknown_facility';
  elsif p_accuracy is null or p_accuracy > c_max_accuracy then
    v_res := 'low_accuracy';
  else
    v_d := distance_m(p_lat, p_lng, v_f.lat, v_f.lng);
    if v_d - least(p_accuracy, c_grace) > v_f.radius_m then
      v_res := 'too_far';
    elsif exists (select 1 from stamps where user_id = v_uid and facility_id = p_facility and stamp_date = v_today) then
      v_res := 'already_today';
    elsif (select count(*) from stamps where user_id = v_uid and stamp_date = v_today) >= c_daily_limit then
      v_res := 'daily_limit';
    else
      select * into v_last from stamps where user_id = v_uid order by stamped_at desc limit 1;
      if found then
        v_km := distance_m(v_last.lat, v_last.lng, p_lat, p_lng) / 1000;
        v_h  := greatest(extract(epoch from (now() - v_last.stamped_at)) / 3600, 1.0 / 60);
        if v_km > 1 and v_km / v_h > c_max_speed_kmh then
          v_res := 'too_fast';
        end if;
      end if;
      v_res := coalesce(v_res, 'ok');
    end if;
  end if;

  insert into checkin_attempts (user_id, facility_id, lat, lng, accuracy_m, distance_m, result)
  values (v_uid, p_facility, p_lat, p_lng, p_accuracy, v_d, v_res);

  if v_res = 'ok' then
    insert into stamps (user_id, facility_id, lat, lng, accuracy_m, distance_m)
    values (v_uid, p_facility, p_lat, p_lng, p_accuracy, v_d);
  end if;

  return jsonb_build_object('ok', v_res = 'ok', 'code', v_res, 'distance_m', round(coalesce(v_d, 0)));
end;
$$;

revoke all on function public.stamp_checkin(text, double precision, double precision, double precision) from public;
grant execute on function public.stamp_checkin(text, double precision, double precision, double precision) to authenticated;
