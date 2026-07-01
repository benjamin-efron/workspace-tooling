local M = {}

-- Find the Hammerspoon screen matching an AeroSpace monitor name.
local function screenForName(name)
    for _, s in ipairs(hs.screen.allScreens()) do
        if s:name() == name then return s end
    end
end

-- Called by workspace-changed.py after AeroSpace has switched focus.
-- Warps the mouse to the new monitor so clicks land in the right place.
-- Skipped when the mouse is already on the target monitor — that means the
-- switch was mouse-driven (e.g. clicking a window on the other monitor), so
-- warping would just yank the cursor away from where the user put it.
function M.onFocus(monitorName)
    local screen = screenForName(monitorName)
                or (hs.window.focusedWindow() and hs.window.focusedWindow():screen())
                or hs.screen.mainScreen()

    if hs.mouse.getCurrentScreen() == screen then return end

    local f = screen:frame()
    hs.mouse.setAbsolutePosition({x = f.x + f.w - 1, y = f.y + f.h - 1})
end

return M
