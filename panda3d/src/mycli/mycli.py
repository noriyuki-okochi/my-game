from panda3d.core import TextNode
from direct.gui.OnscreenText import OnscreenText

class MyCli():
    inputX = 0.1      
    inputY = -1.80    
    inputScale = 0.06
    promptX = 0.1      
    promptY = -1.60    
    promptScale = 0.06
    #
    #   base:ShowBase
    #
    def __init__(self, base, font, 
                 iX = inputX, iY = inputY, iScale = inputScale,
                 pX = promptX,pY = promptY,pScale = promptScale):
        #
        # CLI command input-line
        #
        self.inputBuffer = ''
        self.cursor_pos = 0
        self.inputline = OnscreenText(text="",
                   parent = base.a2dTopLeft, align = TextNode.ALeft,
                   fg = (1, 1, 1, 1), bg = (0, 0, 0, 0.5),
                   pos = (iX, iY), scale = iScale, font = font,
                   shadow = (0, 0, 0, 0.5))
        #
        # prompt display-line
        #  
        self.promptline = OnscreenText(text="",
                   parent = base.a2dTopLeft, align=TextNode.ALeft,
                   fg = (1, 1, 1, 1), 
                   pos = (pX, pY), 
                   scale = pScale, font = font,
                   shadow=(0, 0, 0, 0.5))

    #
    # clear input-line
    #
    def clear(self):
        self.inputBuffer = ''
        self.inputline.setText('')
        self.cursor_pos = 0
        self.promptline.setText('')
        return
    #
    # set start position of input-line
    #
    def start(self, prompt_text = None):
        if prompt_text != None:
            self.promptline.setText(prompt_text)
        #
        self.inputBuffer = ''
        self.inputline.setText(':_')
        self.cursor_pos = 1
        return
    #
    # return input-buffer
    #
    def getBuffer(self):
        return self.inputBuffer
    #
    # append string to inputBuffer and display input-line
    #
    def append(self, str):
        self.inputBuffer += str
        self.cursor_pos += len(str)
        self.inputline.setText(f":{self.inputBuffer}_")
        return self.inputBuffer
    #
    # edit input-line with enterd key
    #
    def input(self, key):
        #print(f"MyCli.input:{key}")
        #
        # edit inputBuffer and move cursor-position
        #
        if key == '\b':     # delete a char. before cursor(backspace )
            if self.cursor_pos > 1:
                buffer = self.inputBuffer[:self.cursor_pos - 2]
                if len(self.inputBuffer) > self.cursor_pos - 1:
                    buffer += self.inputBuffer[self.cursor_pos - 1:]
                self.inputBuffer = buffer
                self.cursor_pos -= 1
        elif key == '':
            self.inputBuffer = ''
            self.cursor_pos = 1
        elif key == '\t':    # cursor right(Right arrow-key)
            if self.cursor_pos < len(self.inputBuffer) + 1:
                self.cursor_pos += 1
        elif key == '\v':    # cursor left(Left arrow-key)
            if self.cursor_pos > 1:
                self.cursor_pos -= 1
        else:
            if self.cursor_pos == len(self.inputBuffer) + 1:
                self.inputBuffer += key
            else:
                buffer = self.inputBuffer[:self.cursor_pos-1]
                buffer += key
                buffer += self.inputBuffer[self.cursor_pos-1:]
                self.inputBuffer = buffer
            self.cursor_pos += 1
        #
        # edit display text
        #
        if self.cursor_pos == len(self.inputBuffer) + 1:
            input_text = f"{self.inputBuffer}_"
        elif self.cursor_pos == 1:
            input_text = f"_{self.inputBuffer}"
        else:
            input_text = self.inputBuffer[:self.cursor_pos-1]
            input_text += '_'
            input_text += self.inputBuffer[self.cursor_pos-1:]
        #
        # display this text to input-line with prompt and coursor
        #  
        self.inputline.setText(f":{input_text}")
        return
    #
    def prompt(self, text):
        return self.promptline.setText(text)
    #
    def clrPrompt(self):
        return self.promptline.setText('')

#       