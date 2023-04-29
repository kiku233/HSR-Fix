
#include <stdio.h>
#include <windows.h>

int main()
{

    HANDLE hToken;
    PROCESS_INFORMATION pi;
    STARTUPINFOW si;
    BOOL bResult;

    // Get a handle to the primary token of the current process
    bResult = OpenProcessToken(GetCurrentProcess(), TOKEN_ALL_ACCESS, &hToken);

    if (!bResult)
    {
        printf("OpenProcessToken failed: %d\n", GetLastError());
        return -1;
    }

    // Initialize the PROCESS_INFORMATION structure
    ZeroMemory(&pi, sizeof(pi));

    // Initialize the STARTUPINFO structure
    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);

    wchar_t* gamepath = L"D:\\softs\\Star Rail\\Game\\StarRail.exe";
    

    // Create a new process as the specified user
    bResult = CreateProcessAsUserW(
        hToken, // user token
        gamepath, // application name
        NULL, // command line
        NULL, // process attributes
        NULL, // thread attributes
        FALSE, // inherit handles
        CREATE_SUSPENDED, // creation flags
        NULL, // environment
        NULL, // current directory
        &si, // startup info
        &pi // process information
    );

    if (!bResult)
    {
        printf("CreateProcessAsUserA failed: %d\n", GetLastError());
        return -1;
    }

    

    printf("游戏启动成功并处于暂停状态，现在去启动你的加载器,启动完成后回来按任意键继续.\n");

    system("pause");

    //ResumeThread
    ResumeThread(pi.hThread);

    // Close the handles
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);
    CloseHandle(hToken);

    return 0;
	//BOOL result = CreateProcessAsUserA(hToken, lpGameNameStr,NULL,NULL,NULL,TRUE, EXTENDED_STARTUPINFO_PRESENT | CREATE_SUSPENDED, NULL, GameFile, (LPSTARTUPINFOA)&si, &pi);
    

}