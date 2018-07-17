#include<bits/stdc++.h>
using namespace std;

int main()
{
    string s;
    int cnt = 0;
    while(cin >> s)
    {
        cnt++;
        if(cnt > 2 or s.length() > 9)
        {
            cout << "NO" << endl;
            return 0;
        }
        long long x = 0;
        for(int i = 0;i < s.length();i++)
        {
            if(!isdigit(s[i]))
            {
                cout << "NO" << endl;
                return 0;
            }
            x = x*10+s[i]-'0';
        }
        if(x > 1e9)
        {
            cout << "NO" << endl;
            return 0;
        }
    }
    if(cnt != 2)   cout << "NO" << endl;
    else    cout << "YES" << endl;
    return 0;
}

