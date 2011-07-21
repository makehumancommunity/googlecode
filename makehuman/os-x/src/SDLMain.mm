/*   SDLMain.m - main entry point for our Cocoa-ized SDL app
       Initial Version: Darrell Walisser <dwaliss1@purdue.edu>
       Non-NIB-Code & other changes: Max Horn <max@quendi.de>

    Feel free to customize this file to suit your needs
*/

#import "SDL/SDL.h"
#import "SDLMain.h"
#import <sys/param.h> /* for MAXPATHLEN */
#import <unistd.h>
#import "AppPreferences.h"
#import "GeneralPreferences.h"
#import <string>

static std::string sModelPath;
static std::string sExportPath;
static std::string sGrabPath;
static std::string sRenderPath;
static std::string sDocumentsPath;

/** Checks if the system is runnin on SnowLeopard (and abov) or below.
 * \return rue if the system is SnowLeopard (OS X 10.6.x) or above, false
 * if it below (e.g. Leopard or Lion...)
 */
static bool isRunningOnSnowLeopardAndAbove()
{
    SInt32 major, minor;
    
    if ((0 == ::Gestalt(gestaltSystemVersionMajor, &major)) &&
        (0 == ::Gestalt(gestaltSystemVersionMinor, &minor)))
        {
            return (major >= 10 && minor >= 6);
        }
        return false;
}

const char* osx_getExportPath()
{
    sExportPath = [[GeneralPreferences exportPath] UTF8String];
    return sExportPath.c_str();
}

const char* osx_getModelPath()
{
    sModelPath = [[GeneralPreferences modelPath] UTF8String];
    return sModelPath.c_str();
}

const char* osx_getGrabPath()
{
    sGrabPath = [[GeneralPreferences grabPath] UTF8String];
    return sGrabPath.c_str();
}

const char* osx_getRenderPath()
{
    sRenderPath = [[GeneralPreferences renderPath] UTF8String];
    return sRenderPath.c_str();
}

const char* osx_getDocumentsPath()
{
    sDocumentsPath = [[GeneralPreferences documentsPath] UTF8String];
    return sDocumentsPath.c_str();
}

#ifndef MAKEHUMAN_AS_MODULE
/* For some reaon, Apple removed setAppleMenu from the headers in 10.4,
 but the method still is there and works. To avoid warnings, we declare
 it ourselves here. */
@interface NSApplication(SDL_Missing_Methods)
- (void)setAppleMenu:(NSMenu *)menu;
@end

/* Use this flag to determine whether we use SDLMain.nib or not */
#define		SDL_USE_NIB_FILE	1

/* Use this flag to determine whether we use CPS (docking) or not */
#define		SDL_USE_CPS		1
#ifdef SDL_USE_CPS
/* Portions of CPS.h */
typedef struct CPSProcessSerNum
{
	UInt32		lo;
	UInt32		hi;
} CPSProcessSerNum;

extern OSErr	CPSGetCurrentProcess( CPSProcessSerNum *psn);
extern OSErr 	CPSEnableForegroundOperation( CPSProcessSerNum *psn, UInt32 _arg2, UInt32 _arg3, UInt32 _arg4, UInt32 _arg5);
extern OSErr	CPSSetFrontProcess( CPSProcessSerNum *psn);

#endif /* SDL_USE_CPS */

static int    gArgc;
static char  **gArgv;
static BOOL   gFinderLaunch;
static BOOL   gCalledAppMainline = FALSE;

static NSString *getApplicationName(void)
{
    NSDictionary *dict;
    NSString *appName = 0;

    /* Determine the application name */
    dict = (NSDictionary *)CFBundleGetInfoDictionary(CFBundleGetMainBundle());
    if (dict)
        appName = [dict objectForKey: @"CFBundleName"];
    
    if (![appName length])
        appName = [[NSProcessInfo processInfo] processName];

    return appName;
}

#if SDL_USE_NIB_FILE
/* A helper category for NSString */
@interface NSString (ReplaceSubString)
- (NSString *)stringByReplacingRange:(NSRange)aRange with:(NSString *)aString;
@end
#endif

@interface SDLApplication : NSApplication
@end


@implementation SDLApplication
/* Invoked from the Quit menu item */
- (void)terminate:(id)sender
{
    /* Post a SDL_QUIT event */
    SDL_Event event;
    event.type = SDL_QUIT;
    SDL_PushEvent(&event);
}

@end

/* The main class of the application, the application's delegate */
@implementation SDLMain

-(void)endSelector:(id)inSender
{
}

-(IBAction)showAbout:(id)inSender
{
    [mAboutPanel makeKeyAndOrderFront:self];
}

-(IBAction)showAcknowledgments:(id)inSender
{
    [mAcknowlegmentPanel makeKeyAndOrderFront:self];
}

-(IBAction)showLicensing:(id)inSender;
{
    [mLicensePanel makeKeyAndOrderFront:self];
}

-(IBAction)showPreferences:(id)inSender
{
	[NSPreferences setDefaultPreferencesClass: [AppPreferences class]];
	[[NSPreferences sharedPreferences] showPreferencesPanel];
}

+(void)openFile:(NSString*)fileName
{
    NSString *s = NSLocalizedStringFromTable(fileName, @"HelpLinks", @"");
    [[NSWorkspace sharedWorkspace] openFile:s];
}

+(void)openURL:(NSString*)urlName
{
    NSString *s = NSLocalizedStringFromTable(urlName, @"HelpLinks", @"");
    [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:s]];
}

-(IBAction)helpFileMHUsersGuide:(id)inSender        {[SDLMain openFile:@"FileMHUsersGuide"];}
-(IBAction)helpFileMHQuickStart:(id)inSender        {[SDLMain openFile:@"FileMHQuickStart"];}

-(IBAction)helpFileMHDevelMHProto:(id)inSender      {[SDLMain openFile:@"FileDevelMHProto"];}

-(IBAction)helpURLMHVisitHome:(id)inSender          {[SDLMain openURL:@"URLMHHome"];}
-(IBAction)helpURLMHVisitForum:(id)inSender         {[SDLMain openURL:@"URLMHForum"];}
-(IBAction)helpURLMHDocuments:(id)inSender          {[SDLMain openURL:@"URLMHDocuments"];}
-(IBAction)helpURLMHArtists:(id)inSender            {[SDLMain openURL:@"URLMHArtists"];}
-(IBAction)helpURLMHSoftwareDownload:(id)inSender   {[SDLMain openURL:@"URLMHUpdate"];}

-(IBAction)helpURLAqsisHome:(id)inSender            {[SDLMain openURL:@"URLAqsisHome"];}
-(IBAction)helpURLAqsisWiki:(id)inSender            {[SDLMain openURL:@"URLAqsisWiki"];}

-(IBAction)helpURLPixieHome:(id)inSender            {[SDLMain openURL:@"URLPixieHome"];}
-(IBAction)helpURLPixieWiki:(id)inSender            {[SDLMain openURL:@"URLPixieWiki"];}
-(IBAction)helpURLPixieInstall:(id)inSender         {[SDLMain openURL:@"URLPixieInstall"];}

-(IBAction)helpURL3DelightHome:(id)inSender         {[SDLMain openURL:@"URL3DelightHome"];}
-(IBAction)helpURL3DelighWiki:(id)inSender          {[SDLMain openURL:@"URL3DelightWiki"];}

/* Set the working directory to the .app's parent directory */
- (void) setupWorkingDirectory:(BOOL)shouldChdir
{
    if (shouldChdir)
    {
        char parentdir[MAXPATHLEN];
		CFURLRef url = CFBundleCopyBundleURL(CFBundleGetMainBundle());
		CFURLRef url2 = CFURLCreateCopyDeletingLastPathComponent(0, url);
		if (CFURLGetFileSystemRepresentation(url2, true, (UInt8 *)parentdir, MAXPATHLEN)) 
        {
            int rc = chdir (parentdir);
	        assert (rc == 0 );   /* chdir to the binary app's parent */
		}
		CFRelease(url);
		CFRelease(url2);
	}

}

#if SDL_USE_NIB_FILE

/* Fix menu to contain the real app name instead of "SDL App" */
- (void)fixMenu:(NSMenu *)aMenu withAppName:(NSString *)appName
{
    NSRange aRange;
    NSEnumerator *enumerator;
    NSMenuItem *menuItem;
   

    aRange = [[aMenu title] rangeOfString:@"SDL App"];
    if (aRange.length != 0)
        [aMenu setTitle: [[aMenu title] stringByReplacingRange:aRange with:appName]];

    enumerator = [[aMenu itemArray] objectEnumerator];
    while ((menuItem = [enumerator nextObject]))
    {
        aRange = [[menuItem title] rangeOfString:@"SDL App"];
        if (aRange.length != 0)
            [menuItem setTitle: [[menuItem title] stringByReplacingRange:aRange with:appName]];
        if ([menuItem hasSubmenu])
            [self fixMenu:[menuItem submenu] withAppName:appName];
    }
    [ aMenu sizeToFit ];
}

#else

static void setApplicationMenu(void)
{
    /* warning: this code is very odd */
    NSMenu *appleMenu;
    NSMenuItem *menuItem;
    NSString *title;
    NSString *appName;
    
    appName = getApplicationName();
    appleMenu = [[NSMenu alloc] initWithTitle:@""];
    
    /* Add menu items */
    title = [@"About " stringByAppendingString:appName];
    [appleMenu addItemWithTitle:title action:@selector(orderFrontStandardAboutPanel:) keyEquivalent:@""];

    [appleMenu addItem:[NSMenuItem separatorItem]];

    title = [@"Hide " stringByAppendingString:appName];
    [appleMenu addItemWithTitle:title action:@selector(hide:) keyEquivalent:@"h"];

    menuItem = (NSMenuItem *)[appleMenu addItemWithTitle:@"Hide Others" action:@selector(hideOtherApplications:) keyEquivalent:@"h"];
    [menuItem setKeyEquivalentModifierMask:(NSAlternateKeyMask|NSCommandKeyMask)];

    [appleMenu addItemWithTitle:@"Show All" action:@selector(unhideAllApplications:) keyEquivalent:@""];

    [appleMenu addItem:[NSMenuItem separatorItem]];

    title = [@"Quit " stringByAppendingString:appName];
    [appleMenu addItemWithTitle:title action:@selector(terminate:) keyEquivalent:@"q"];

    
    /* Put menu into the menubar */
    menuItem = [[NSMenuItem alloc] initWithTitle:@"" action:nil keyEquivalent:@""];
    [menuItem setSubmenu:appleMenu];
    [[NSApp mainMenu] addItem:menuItem];

    /* Tell the application object that this is now the application menu */
    [NSApp setAppleMenu:appleMenu];

    /* Finally give up our references to the objects */
    [appleMenu release];
    [menuItem release];
}

/* Create a window menu */
static void setupWindowMenu(void)
{
    NSMenu      *windowMenu;
    NSMenuItem  *windowMenuItem;
    NSMenuItem  *menuItem;

    windowMenu = [[NSMenu alloc] initWithTitle:@"Window"];
    
    /* "Minimize" item */
    menuItem = [[NSMenuItem alloc] initWithTitle:@"Minimize" action:@selector(performMiniaturize:) keyEquivalent:@"m"];
    [windowMenu addItem:menuItem];
    [menuItem release];
    
    /* Put menu into the menubar */
    windowMenuItem = [[NSMenuItem alloc] initWithTitle:@"Window" action:nil keyEquivalent:@""];
    [windowMenuItem setSubmenu:windowMenu];
    [[NSApp mainMenu] addItem:windowMenuItem];
    
    /* Tell the application object that this is now the window menu */
    [NSApp setWindowsMenu:windowMenu];

    /* Finally give up our references to the objects */
    [windowMenu release];
    [windowMenuItem release];
}

/* Replacement for NSApplicationMain */
static void CustomApplicationMain (int argc, char **argv)
{
    NSAutoreleasePool	*pool = [[NSAutoreleasePool alloc] init];
    SDLMain				*sdlMain;

    /* Ensure the application object is initialised */
    [SDLApplication sharedApplication];
    
#ifdef SDL_USE_CPS
    {
        CPSProcessSerNum PSN;
        /* Tell the dock about us */
        if (!CPSGetCurrentProcess(&PSN))
            if (!CPSEnableForegroundOperation(&PSN,0x03,0x3C,0x2C,0x1103))
                if (!CPSSetFrontProcess(&PSN))
                    [SDLApplication sharedApplication];
    }
#endif /* SDL_USE_CPS */

    /* Set up the menubar */
    [NSApp setMainMenu:[[NSMenu alloc] init]];
    setApplicationMenu();
    setupWindowMenu();

    /* Create SDLMain and make it the app delegate */
    sdlMain = [[SDLMain alloc] init];
    [NSApp setDelegate:sdlMain];
    
    /* Start the main event loop */
    [NSApp run];
    
    [sdlMain release];
    [pool release];
}

#endif


/*
 * Catch document open requests...this lets us notice files when the app
 *  was launched by double-clicking a document, or when a document was
 *  dragged/dropped on the app's icon. You need to have a
 *  CFBundleDocumentsType section in your Info.plist to get this message,
 *  apparently.
 *
 * Files are added to gArgv, so to the app, they'll look like command line
 *  arguments. Previously, apps launched from the finder had nothing but
 *  an argv[0].
 *
 * This message may be received multiple times to open several docs on launch.
 *
 * This message is ignored once the app's mainline has been called.
 */
- (BOOL)application:(NSApplication *)theApplication openFile:(NSString *)filename
{
    const char *temparg;
    size_t arglen;
    char *arg;
    char **newargv;

    if (!gFinderLaunch)  /* MacOS is passing command line args. */
        return FALSE;

    if (gCalledAppMainline)  /* app has started, ignore this document. */
        return FALSE;

    temparg = [filename UTF8String];
    arglen = SDL_strlen(temparg) + 1;
    arg = (char *) SDL_malloc(arglen);
    if (arg == NULL)
        return FALSE;

    newargv = (char **) realloc(gArgv, sizeof (char *) * (gArgc + 2));
    if (newargv == NULL)
    {
        SDL_free(arg);
        return FALSE;
    }
    gArgv = newargv;

    SDL_strlcpy(arg, temparg, arglen);
    gArgv[gArgc++] = arg;
    gArgv[gArgc] = NULL;
    return TRUE;
}

/* Called when the internal event loop has just started running */
- (void) applicationDidFinishLaunching: (NSNotification *) note
{
    int status;

    /* Set the working directory to the .app's parent directory */
    [self setupWorkingDirectory:gFinderLaunch];

#if SDL_USE_NIB_FILE
    /* Set the main menu to contain the real app name instead of "SDL App" */
    [self fixMenu:[NSApp mainMenu] withAppName:getApplicationName()];
    licenseWindowVisible = false; // The licensing panel should not be visible at launch time
#endif

//#define CHECK_PYTHON_VERSION
#ifdef CHECK_PYTHON_VERSION
    /* Perform a version check of the installed Python interpreter.
     * If it is older than 3.x The User will be notified to update it.
     */
    const char* kPythonVersionNumber = Py_GetVersion();
    int major, minor, sub;
    const int rc(::sscanf(kPythonVersionNumber, "%d.%d.%d", &major, &minor, &sub));

    if ((rc == 3) && !((major >= 3) && (minor >= 2)))
    {
        NSString *messageString = [NSString stringWithFormat:
                                   @"Please update to Python 3.x as soon as possible!\n\n"
                                    "Makehuman will use some extended Functionality of Python 3.x in the near future.\n\n"
                                    "You are currently using Python V%d.%d.%d\n\n"
                                    "So please update the Python on your machine as soon as possible!",major, minor, sub];
        
        const NSInteger rc = NSRunInformationalAlertPanel(@"Alert Message", 
                                                          messageString, 
                                                          @"Start it anyway!", 
                                                          @"Visit the Python Website...", 
                                                          @"Download the Python installer...");
        switch(rc)
        {
            case NSAlertDefaultReturn :
                break;
                
            case NSAlertAlternateReturn :
                [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://www.python.org/download"]];
                break;

            case NSAlertOtherReturn :
                [[NSWorkspace sharedWorkspace] 
                    openURL:[NSURL URLWithString:isRunningOnSnowLeopardAndAbove() ? 
                                            @"http://www.python.org/ftp/python/3.2/python-3.2-macosx10.6.dmg" :
                                            @"http://www.python.org/ftp/python/3.2/python-3.2-macosx10.3.dmg"]];
                break;
        }
        printf("rc is %d\n", rc);
            //        printf("Please update to Python 3.x as soon as possible!\n");
    }
#endif // #ifdef CHECK_PYTHON_VERSION
    
    /* Hand off to main application code */
    gCalledAppMainline = TRUE;
    status = SDL_main (gArgc, gArgv);

    NSUserDefaults *userDefaults = [NSUserDefaults standardUserDefaults];
    /* Store the User defaults */
    [userDefaults synchronize];

    /* We're done, thank you for playing */
    exit(status);
}

@synthesize licenseWindowVisible;

@end /* @implementation SDLMain */


@implementation NSString (ReplaceSubString)

- (NSString *)stringByReplacingRange:(NSRange)aRange with:(NSString *)aString
{
    unsigned int bufferSize;
    unsigned int selfLen = [self length];
    unsigned int aStringLen = [aString length];
    unichar *buffer;
    NSRange localRange;
    NSString *result;

    bufferSize = selfLen + aStringLen - aRange.length;
    buffer = (unichar*)NSAllocateMemoryPages(bufferSize*sizeof(unichar));
    
    /* Get first part into buffer */
    localRange.location = 0;
    localRange.length = aRange.location;
    [self getCharacters:buffer range:localRange];
    
    /* Get middle part into buffer */
    localRange.location = 0;
    localRange.length = aStringLen;
    [aString getCharacters:(buffer+aRange.location) range:localRange];
     
    /* Get last part into buffer */
    localRange.location = aRange.location + aRange.length;
    localRange.length = selfLen - localRange.location;
    [self getCharacters:(buffer+aRange.location+aStringLen) range:localRange];
    
    /* Build output string */
    result = [NSString stringWithCharacters:buffer length:bufferSize];
    
    NSDeallocateMemoryPages(buffer, bufferSize);
    
    return result;
}

@end

#ifdef main
#  undef main
#endif

/* Main entry point to executable - should *not* be SDL_main! */
int main (int argc, char **argv)
{
    /* Copy the arguments into a global variable */
    /* This is passed if we are launched by double-clicking */
    if ( argc >= 2 && strncmp (argv[1], "-psn", 4) == 0 ) {
        gArgv = (char **) SDL_malloc(sizeof (char *) * 2);
        gArgv[0] = argv[0];
        gArgv[1] = NULL;
        gArgc = 1;
        gFinderLaunch = YES;
    } else {
        int i;
        gArgc = argc;
        gArgv = (char **) SDL_malloc(sizeof (char *) * (argc+1));
        for (i = 0; i <= argc; i++)
            gArgv[i] = argv[i];
        gFinderLaunch = NO;
    }

    int rc = osx_adjustWorkingDir(argv[0]);
    assert(0 == rc);
    
    /* Adjust the environment vars for the external renderer */
    rc = osx_adjustRenderEnvironment();
    assert(0 == rc);

#if SDL_USE_NIB_FILE
    [SDLApplication poseAsClass:[NSApplication class]];

    NSApplicationMain ((int)argc, (const char**)argv);
#else
    CustomApplicationMain (argc, argv);
#endif
    return 0;
}

#endif // #ifndef MAKEHUMAN_AS_MODULE

extern "C" int isMainWindowActive();
// Check weather the current focus window is the main window
int isMainWindowActive()
{
    const NSWindow *keyWin  = [NSApp keyWindow];
    
    // is the key window valid?
    if (keyWin == NULL)
        return false; // No? then The main Window is not the active one.
    
    // Get the Key Windows title
    const NSString *title = [keyWin title];
    
    // The MainWindow is active only if the key window is the MainWindow 
    // (whose title is "MakeHuman").
    const NSRange range([title rangeOfString:@"MakeHuman"]);
    return range.location == 0 && range.length > 0;
}

