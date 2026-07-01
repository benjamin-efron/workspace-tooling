local M = {}

local AEROSPACE = '/opt/homebrew/bin/aerospace'
local TMUX_BIN  = '/opt/homebrew/bin/tmux'

-- ── Layout ────────────────────────────────────────────────────────────────────
local W        = 560
local HEADER_H = 52
local ITEM_H   = 52
local PAD      = 20
local MARGIN_R = 20
local MARGIN_T = 40
local CORNER_R = 14

-- ── Colors ────────────────────────────────────────────────────────────────────
local C_BG_IDLE  = {red=0.08, green=0.08, blue=0.10, alpha=0.88}
local C_BG_FOCUS = {red=0.05, green=0.12, blue=0.25, alpha=0.94}
local C_SEL      = {red=0.18, green=0.38, blue=0.65, alpha=1.0}
local C_HEADER   = {red=0.75, green=0.85, blue=1.0,  alpha=1.0}
local C_TEXT     = {red=1.0,  green=1.0,  blue=1.0,  alpha=0.9}
local C_DIM      = {red=0.5,  green=0.5,  blue=0.5,  alpha=1.0}

-- ── State ─────────────────────────────────────────────────────────────────────
local HIDDEN  = 'hidden'
local VISIBLE = 'visible'   -- notification arrived, not keyboard-focused
local FOCUSED = 'focused'

-- Each entry: {session_id, label, workspace, tmux_pane}
local notifications = {}
local state         = HIDDEN
local selectedIdx   = 1
local modal         = hs.hotkey.modal.new()

-- Canvas is stored in a global so reloads can destroy the previous instance.
if _G._cnHudCanvas then
    pcall(function() _G._cnHudCanvas:delete() end)
    _G._cnHudCanvas = nil
end
local canvas = nil

-- ── Helpers ───────────────────────────────────────────────────────────────────
local function clamp(v, lo, hi) return math.max(lo, math.min(hi, v)) end

local function focusedScreen()
    local win = hs.window.focusedWindow()
    if win then return win:screen() end
    return hs.screen.mainScreen()
end

local function render()
    if canvas then canvas:delete(); canvas = nil end
    if state == HIDDEN then return end

    local sf = focusedScreen():frame()
    local n  = #notifications
    local h  = HEADER_H + math.max(n, 1) * ITEM_H + 8

    canvas = hs.canvas.new({
        x = sf.x + sf.w - W - MARGIN_R,
        y = sf.y + MARGIN_T,
        w = W, h = h,
    })
    _G._cnHudCanvas = canvas
    canvas:level(hs.canvas.windowLevels.overlay)

    -- Background
    canvas[#canvas+1] = {
        type             = 'rectangle', action = 'fill',
        fillColor        = state == FOCUSED and C_BG_FOCUS or C_BG_IDLE,
        roundedRectRadii = {xRadius=CORNER_R, yRadius=CORNER_R},
        frame            = {x=0, y=0, w=W, h=h},
    }

    -- Header
    canvas[#canvas+1] = {
        type='text', textAlignment='left',
        textFont='Helvetica-Bold', textSize=20, textColor=C_HEADER,
        text  = n > 0 and ('Claude  (' .. n .. ')') or 'Claude',
        frame = {x=PAD, y=14, w=W-PAD*2, h=26},
    }

    if n == 0 then
        canvas[#canvas+1] = {
            type='text', textAlignment='center',
            textFont='Helvetica', textSize=17, textColor=C_DIM,
            text  = 'No pending sessions',
            frame = {x=0, y=HEADER_H+8, w=W, h=ITEM_H-8},
        }
    else
        for i, notif in ipairs(notifications) do
            local iy = HEADER_H + (i-1)*ITEM_H
            if state == FOCUSED and i == selectedIdx then
                canvas[#canvas+1] = {
                    type='rectangle', action='fill', fillColor=C_SEL,
                    frame={x=2, y=iy, w=W-4, h=ITEM_H},
                }
            end
            canvas[#canvas+1] = {
                type='text', textAlignment='left',
                textFont='Helvetica-Bold', textSize=18, textColor=C_TEXT,
                text  = notif.label,
                frame = {x=PAD, y=iy+14, w=W-PAD*2, h=24},
            }
        end
    end

    canvas:show()
end

local function hide()
    state = HIDDEN
    modal:exit()
    render()
end

local function navigate(notif)
    print('cn navigate: ws=' .. tostring(notif.workspace) .. ' pane=' .. tostring(notif.tmux_pane)
        .. ' winId=' .. tostring(notif.window_id))

    -- Phase 3: switch to the tmux window (called after phase 1/2 completes).
    local function phase3()
        print('cn phase3: tmux switch')
        if notif.tmux_pane ~= '' then
            hs.timer.doAfter(0.10, function()
                hs.task.new(TMUX_BIN, nil,
                    {'switch-client', '-t', notif.tmux_pane}):start()
            end)
        end
    end

    -- Phase 2: navigate to the workspace. Only used as a fallback when no
    -- window-id was resolved — when phase 1 runs, `focus --window-id` already
    -- switches to the window's workspace/monitor as a side effect, and issuing
    -- a redundant `workspace` call after it caused a focus/revert flash.
    local function phase2()
        print('cn phase2: aerospace workspace ' .. tostring(notif.workspace))
        hs.task.new(AEROSPACE, function() phase3() end,
            {'workspace', notif.workspace}):start()
    end

    -- Phase 1: focus the monitor by focusing the exact terminal window that fired
    -- this notification (resolved by notify.py), via AeroSpace's own `focus`
    -- command so its internal state stays consistent (not hs.window():focus()).
    local function phase1()
        if notif.window_id then
            print('cn phase1: aerospace focus --window-id ' .. tostring(notif.window_id))
            hs.task.new(AEROSPACE, function() phase3() end,
                {'focus', '--window-id', tostring(notif.window_id)}):start()
        else
            print('cn phase1: no window_id, skipping to phase2')
            phase2()
        end
    end
    phase1()

    -- Clear all notifications for this session and hide
    local sid  = notif.session_id
    local kept = {}
    for _, n in ipairs(notifications) do
        if n.session_id ~= sid then kept[#kept+1] = n end
    end
    notifications = kept
    selectedIdx   = clamp(selectedIdx, 1, math.max(#notifications, 1))
    hide()
end

-- ── Modal keyboard controls (active only when HUD is focused) ─────────────────
modal:bind('', 'j', function()
    selectedIdx = clamp(selectedIdx+1, 1, math.max(#notifications, 1))
    render()
end)

modal:bind('', 'k', function()
    selectedIdx = clamp(selectedIdx-1, 1, math.max(#notifications, 1))
    render()
end)

modal:bind('', 'd', function()
    if #notifications > 0 then
        table.remove(notifications, selectedIdx)
        selectedIdx = clamp(selectedIdx, 1, math.max(#notifications, 1))
        if #notifications == 0 then hide() else render() end
    end
end)

modal:bind('', 'return', function()
    if #notifications > 0 then
        navigate(notifications[selectedIdx])
    end
end)

-- ── Public API ────────────────────────────────────────────────────────────────

function M.addFromFile(path)
    local f = io.open(path, 'r')
    if not f then return end
    local content = f:read('*all')
    f:close()
    os.remove(path)

    local data = hs.json.decode(content)
    if not data or not data.session_id then return end

    local label = data.label or data.session_id:sub(1, 12)

    local kept = {}
    for _, n in ipairs(notifications) do
        if n.session_id ~= data.session_id then kept[#kept+1] = n end
    end
    table.insert(kept, 1, {
        session_id = data.session_id,
        label      = label,
        workspace  = data.workspace or '',
        tmux_pane  = data.tmux_pane or '',
        window_id  = data.window_id,
    })
    notifications = kept
    selectedIdx   = 1

    -- Show as visible-unfocused if currently hidden; don't steal focus
    if state == HIDDEN then state = VISIBLE end
    render()
end

function M.toggle()
    if state == FOCUSED then
        hide()
    else
        -- HIDDEN or VISIBLE → FOCUSED
        state = FOCUSED
        modal:enter()
        render()
    end
end

-- Hyper-n toggles the HUD
hs.hotkey.bind({'cmd','ctrl','alt','shift'}, 'n', function() M.toggle() end)

-- Watch for notification files dropped by the Claude Code hook.
-- Using pathwatcher avoids the hs -c IPC recursion problem.
-- Stored in _G so Lua's GC doesn't collect the FSEvents stream after module load.
local NOTIFY_DIR = os.getenv('HOME') .. '/.hammerspoon/notifications'
hs.fs.mkdir(NOTIFY_DIR)
if _G._cnNotifyWatcher then pcall(function() _G._cnNotifyWatcher:stop() end) end
_G._cnNotifyWatcher = hs.pathwatcher.new(NOTIFY_DIR, function(paths)
    for _, path in ipairs(paths) do
        if path:match('%.json$') then
            M.addFromFile(path)
        end
    end
end)
_G._cnNotifyWatcher:start()

return M
