// ViewController.m
//
// Copyright (c) 2014 Auth0 (http://auth0.com)
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.

#import "ViewController.h"
#import "Application.h"

#import <Lock/Lock.h>
#import <JWTDecode/A0JWTDecoder.h>
#import <MBProgressHUD/MBProgressHUD.h>
#import <SimpleKeychain/A0SimpleKeychain.h>

@interface ViewController ()

@end

@implementation ViewController

- (void)viewDidLoad {
    [super viewDidLoad];
    A0SimpleKeychain *store = [Application sharedInstance].store;
    NSString *idToken = [store stringForKey:@"id_token"];
    if (idToken) {
        if ([A0JWTDecoder isJWTExpired:idToken]) {
            NSString *refreshToken = [store stringForKey:@"refresh_token"];
            [MBProgressHUD showHUDAddedTo:self.view animated:YES];
            A0APIClient *client = [[[Application sharedInstance] lock] apiClient];
            [client fetchNewIdTokenWithRefreshToken:refreshToken parameters:nil success:^(A0Token *token) {
                [store setString:token.idToken forKey:@"id_token"];
                [MBProgressHUD hideHUDForView:self.view animated:YES];
                [self performSegueWithIdentifier:@"showProfile" sender:self];
            } failure:^(NSError *error) {
                [store clearAll];
                [MBProgressHUD hideHUDForView:self.view animated:YES];
            }];
        } else {
            [self performSegueWithIdentifier:@"showProfile" sender:self];
        }
    }
}

- (IBAction)showSignIn:(id)sender {
    A0Lock *lock = [[Application sharedInstance] lock];
    A0LockViewController *controller = [lock newLockViewController];
    controller.closable = true;
    controller.onAuthenticationBlock = ^(A0UserProfile *profile, A0Token *token) {
        
        A0SimpleKeychain *keychain = [Application sharedInstance].store;
        [keychain setString:token.idToken forKey:@"id_token"];
        [keychain setString:token.refreshToken forKey:@"refresh_token"];
        [keychain setData:[NSKeyedArchiver archivedDataWithRootObject:profile] forKey:@"profile"];
        [self dismissViewControllerAnimated:YES completion:nil];
        [self performSegueWithIdentifier:@"showProfile" sender:self];
    };
    [self presentViewController:controller animated:YES completion:nil];
}

@end
