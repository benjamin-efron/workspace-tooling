local M = {}

local FLASH_COLOR    = {alpha = 0.9, red = 0.3, green = 0.75, blue = 1.0}
local FLASH_WIDTH    = 4
local FLASH_DURATION = 0.2
local COOLDOWN       = 0.3

local lastFlash   = 0
local activeCanvas = nil
local activeTimer  = nil

function M.show()
    local now = hs.timer.secondsSinceEpoch()
    if now - lastFlash < COOLDOWN then return end
    lastFlash = now

    if activeTimer  then activeTimer:stop();  activeTimer  = nil end
    if activeCanvas then activeCanvas:delete(); activeCanvas = nil end

    local win = hs.window.focusedWindow()
    if not win then return end

    local frame = win:frame()
    local inset = FLASH_WIDTH / 2
    local canvas = hs.canvas.new(frame)
    canvas[1] = {
        type        = "rectangle",
        action      = "stroke",
        strokeColor = FLASH_COLOR,
        strokeWidth = FLASH_WIDTH,
        frame       = {x = inset, y = inset, w = frame.w - FLASH_WIDTH, h = frame.h - FLASH_WIDTH},
    }
    canvas:level(hs.canvas.windowLevels.overlay)
    canvas:show()

    activeCanvas = canvas
    activeTimer  = hs.timer.doAfter(FLASH_DURATION, function()
        canvas:delete()
        activeCanvas = nil
        activeTimer  = nil
    end)
end

return M
