#!/usr/bin/env bash
# Deterministic tests for redundancy-guard.sh
# Usage: test-redundancy-guard.sh <path-to-hook>
# Reproduces the taimei-auth PR #142 false positive (縮約置換) plus non-regression cases.
set -u

HOOK="$1"
WORK=$(mktemp -d)
PASS=0; FAIL=0

run_hook() { # $1=file $2=session_id ; sets HOOK_EXIT / HOOK_ERR
  local out
  out=$(printf '{"tool_input":{"file_path":"%s"},"session_id":"%s"}' "$1" "$2" \
        | bash "$HOOK" 2>&1 >/dev/null)
  HOOK_EXIT=$?
  HOOK_ERR="$out"
}

check() { # $1=name $2=expected_exit
  if [ "$HOOK_EXIT" = "$2" ]; then
    echo "PASS: $1 (exit=$HOOK_EXIT)"
    PASS=$((PASS+1))
  else
    echo "FAIL: $1 (expected exit=$2, got exit=$HOOK_EXIT)"
    printf '%s\n' "  stderr: $HOOK_ERR" | head -3
    FAIL=$((FAIL+1))
  fi
}

mkrepo() { # $1=name -> echoes repo dir
  local d="$WORK/$1"
  mkdir -p "$d"
  git -C "$d" init -q
  git -C "$d" config user.email t@t && git -C "$d" config user.name t
  echo "$d"
}

# --- Case 1: 縮約置換 (13 comment lines -> 6) must NOT fire ---------------
R=$(mkrepo case1)
{
  for i in $(seq 1 13); do echo "# why line $i"; done
  echo "def mfa_challenge(user)"
  echo "  user.two_factor_enabled"
  echo "end"
} > "$R/policy.rb"
git -C "$R" add . && git -C "$R" commit -qm init
{
  for i in $(seq 1 6); do echo "# condensed why $i"; done
  echo "def mfa_challenge(user)"
  echo "  user.two_factor_enabled"
  echo "end"
} > "$R/policy.rb"
run_hook "$R/policy.rb" "s1"
check "縮約置換 (net -7) は発火しない" 0

# --- Case 2: 縮約セッション中の追い Edit (net なお負) も発火しない --------
{
  for i in $(seq 1 8); do echo "# condensed why $i"; done
  echo "def mfa_challenge(user)"
  echo "  user.two_factor_enabled"
  echo "end"
} > "$R/policy.rb"
run_hook "$R/policy.rb" "s1"
check "縮約後の追い Edit (net -5) も発火しない" 0

# --- Case 3: 純追加 (net +3) は発火する -----------------------------------
R=$(mkrepo case3)
printf 'def calc(x)\n  x * 2\nend\n' > "$R/calc.rb"
git -C "$R" add . && git -C "$R" commit -qm init
printf '# note a\n# note b\n# note c\ndef calc(x)\n  x * 2\nend\n' > "$R/calc.rb"
run_hook "$R/calc.rb" "s3"
check "純追加 (net +3) は発火する" 2

# --- Case 4: 同数書き換え (net 0) は発火しない (許容 trade-off) -----------
R=$(mkrepo case4)
printf '# old why 1\n# old why 2\ndef calc(x)\n  x\nend\n' > "$R/calc.rb"
git -C "$R" add . && git -C "$R" commit -qm init
printf '# new why 1\n# new why 2\ndef calc(x)\n  x\nend\n' > "$R/calc.rb"
run_hook "$R/calc.rb" "s4"
check "同数書き換え (net 0) は発火しない" 0

# --- Case 5: 段階的な純追加は成長分だけ再発火する -------------------------
R=$(mkrepo case5)
printf 'def f(x)\n  x\nend\n' > "$R/f.rb"
git -C "$R" add . && git -C "$R" commit -qm init
printf '# a\n# b\ndef f(x)\n  x\nend\n' > "$R/f.rb"
run_hook "$R/f.rb" "s5"
check "1回目の追加 (net +2) は発火する" 2
printf '# a\n# b\n# c\n# d\n# e\ndef f(x)\n  x\nend\n' > "$R/f.rb"
run_hook "$R/f.rb" "s5"
check "成長 (net +2 -> +5) は再発火する" 2
run_hook "$R/f.rb" "s5"
check "同一カウントの再 Edit は再発火しない (dedup)" 0

# --- Case 6: untracked 新規ファイルは全行カウント (従来どおり発火) --------
R=$(mkrepo case6)
printf 'def g(x)\n  x\nend\n' > "$R/existing.rb"
git -C "$R" add . && git -C "$R" commit -qm init
printf '# why 1\n# why 2\n# why 3\ndef h(x)\n  x\nend\n' > "$R/new_file.rb"
run_hook "$R/new_file.rb" "s6"
check "untracked 新規ファイルのコメントは発火する" 2

# --- Case 7: suppression 追加は発火する -----------------------------------
R=$(mkrepo case7)
printf 'def j(x)\n  x\nend\n' > "$R/j.rb"
git -C "$R" add . && git -C "$R" commit -qm init
printf 'def j(x) # rubocop:disable Style/Foo\n  x\nend\n' > "$R/j.rb"
run_hook "$R/j.rb" "s7"
check "suppression 追加は発火する" 2

echo "---"
echo "PASS=$PASS FAIL=$FAIL"
rm -r "$WORK"
[ "$FAIL" = 0 ]
