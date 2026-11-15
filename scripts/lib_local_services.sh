# shellcheck shell=bash
# Arrêt des services Python locaux (fichiers .run/*.pid + orphelins même dépôt).
# Usage : source depuis bootstrap_local.sh / bootstrap_stop.sh avec ROOT défini.

momoshield__proc_cmdline() {
  local pid="$1"
  tr '\0' ' ' <"/proc/$pid/cmdline" 2>/dev/null || true
}

momoshield__proc_cwd() {
  local pid="$1"
  readlink -f "/proc/$pid/cwd" 2>/dev/null || true
}

# Tue les PIDs dont le cwd == ROOT et la cmdline contient $needle.
momoshield_stop_matching() {
  local root="$1"
  local needle="$2"
  local pid cwd cmdline

  while read -r pid; do
    [[ -z "$pid" ]] && continue
    [[ "$pid" == "$$" ]] && continue
    cwd="$(momoshield__proc_cwd "$pid")"
    [[ "$cwd" == "$root" ]] || continue
    cmdline="$(momoshield__proc_cmdline "$pid")"
    [[ "$cmdline" == *"$needle"* ]] || continue
    kill -TERM "$pid" 2>/dev/null || true
  done < <(pgrep -f "$needle" 2>/dev/null || true)
}

momoshield_wait_gone() {
  local root="$1"
  local needle="$2"
  local deadline=$((SECONDS + 15))
  local pid cwd cmdline

  while (( SECONDS < deadline )); do
  local remaining=0
  while read -r pid; do
    [[ -z "$pid" ]] && continue
    cwd="$(momoshield__proc_cwd "$pid")"
    [[ "$cwd" == "$root" ]] || continue
    cmdline="$(momoshield__proc_cmdline "$pid")"
    [[ "$cmdline" == *"$needle"* ]] || continue
    remaining=1
    break
  done < <(pgrep -f "$needle" 2>/dev/null || true)
    (( remaining == 0 )) && return 0
    sleep 0.5
  done

  while read -r pid; do
    [[ -z "$pid" ]] && continue
    cwd="$(momoshield__proc_cwd "$pid")"
    [[ "$cwd" == "$root" ]] || continue
    cmdline="$(momoshield__proc_cmdline "$pid")"
    [[ "$cmdline" == *"$needle"* ]] || continue
    kill -KILL "$pid" 2>/dev/null || true
  done < <(pgrep -f "$needle" 2>/dev/null || true)
}

momoshield_stop_streamlit() {
  local root="$1"
  local pid cwd cmdline

  while read -r pid; do
    [[ -z "$pid" ]] && continue
    [[ "$pid" == "$$" ]] && continue
    cwd="$(momoshield__proc_cwd "$pid")"
    [[ "$cwd" == "$root" ]] || continue
    cmdline="$(momoshield__proc_cmdline "$pid")"
    [[ "$cmdline" == *"dashboards/app.py"* ]] || continue
    kill -TERM "$pid" 2>/dev/null || true
  done < <(pgrep -f "dashboards/app.py" 2>/dev/null || true)
}

# Arrêt complet : PID files + tous les processus liés à ce clone du repo.
momoshield_stop_local_services() {
  local root="${1:?root}"
  local run_dir="${2:-$root/.run}"

  if [[ -f "$run_dir/consumer.pid" ]]; then
    kill "$(cat "$run_dir/consumer.pid")" 2>/dev/null || true
  fi
  if [[ -f "$run_dir/producer.pid" ]]; then
    kill "$(cat "$run_dir/producer.pid")" 2>/dev/null || true
  fi
  if [[ -f "$run_dir/streamlit.pid" ]]; then
    kill "$(cat "$run_dir/streamlit.pid")" 2>/dev/null || true
  fi

  momoshield_stop_matching "$root" "streaming.python_consumer"
  momoshield_stop_matching "$root" "producer.main"
  momoshield_stop_streamlit "$root"

  momoshield_wait_gone "$root" "streaming.python_consumer"
  momoshield_wait_gone "$root" "producer.main"
  momoshield_wait_gone "$root" "dashboards/app.py"

  rm -f "$run_dir/consumer.pid" "$run_dir/producer.pid" "$run_dir/streamlit.pid"
}

momoshield_count_repo_processes() {
  local root="$1"
  local needle="$2"
  local count=0 pid cwd cmdline

  while read -r pid; do
    [[ -z "$pid" ]] && continue
    cwd="$(momoshield__proc_cwd "$pid")"
    [[ "$cwd" == "$root" ]] || continue
    cmdline="$(momoshield__proc_cmdline "$pid")"
    [[ "$cmdline" == *"$needle"* ]] || continue
    count=$((count + 1))
  done < <(pgrep -f "$needle" 2>/dev/null || true)
  echo "$count"
}