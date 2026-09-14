    -- Tasks the autonomous Strands "back-office concierge" surfaces for staff.
    -- The agent writes these with the service-role key (bypasses RLS); the dashboard
    -- reads them scoped to the business owner/members.
    create table if not exists agent_tasks (
    id uuid primary key default gen_random_uuid(),
    business_id uuid references businesses not null,
    title text not null,
    detail text,
    severity text not null default 'review' check (severity in ('info','review','urgent')),
    status text not null default 'open' check (status in ('open','done','dismissed')),
    created_at timestamptz default now()
    );

    alter table agent_tasks enable row level security;

    create policy "members read agent_tasks" on agent_tasks
    for select using (
        is_business_member(business_id)
        or exists (select 1 from businesses b where b.id = business_id and b.owner_user_id = auth.uid())
    );

    create policy "members update agent_tasks" on agent_tasks
    for update using (
        is_business_member(business_id)
        or exists (select 1 from businesses b where b.id = business_id and b.owner_user_id = auth.uid())
    );

    create index if not exists idx_agent_tasks_business on agent_tasks (business_id, created_at desc);
