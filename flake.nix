{
  description = "android autoconfiguration experiment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    (flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        # uiautomator
        uiautomator = pkgs.python3Packages.buildPythonPackage {
          pname = "uiautomator";
          version = "20201016";
          src = pkgs.fetchFromGitHub {
            owner = "xiaocong";
            repo = "uiautomator";
            rev = "ddef372b5bd3811f196290a1f75b636c6be9da2b";
            sha256 = "sha256-tSgI7JAhBU5oYXrv1KjZx4ZgIX2y1qw9W7XbYNKs0RI=";
          };
          propagatedBuildInputs = with pkgs.python3Packages; [
            urllib3
          ];
          doCheck = false;
        };

        # fdroidcl
        fdroidcl = pkgs.buildGoModule rec {
          pname = "fdroidcl";
          version = "0.5.0";

          src = pkgs.fetchFromGitHub {
            owner = "mvdan";
            repo = pname;
            rev = "v${version}";
            sha256 = "sha256-wEP4Ed2G4OTfTD+sayWMPUGmdzxcmJYoBp8MKbxvrOc=";
          };

          vendorHash = "sha256-uwfVjSXSroIY2xv1ETTGv1TxfMXaFL9IQ1wcMzh5/jY=";
          doCheck = false;
        };

        droidctl = pkgs.python3Packages.buildPythonPackage {
          pname = "droidctl";
          version = "0.0.1";
          src = ./.;
          propagatedBuildInputs = with pkgs.python3Packages; [
            uiautomator
            pure-python-adb
            click
            fdroidcl
          ] ++ (with pkgs; [
            androidenv.androidPkgs_9_0.platform-tools
          ]);
          doCheck = false;
        };

        pythonEnv = pkgs.python3.withPackages (ps: with ps; [
          droidctl
          click
          uiautomator
          pure-python-adb
        ]);

        devShell = pkgs.mkShell {
          buildInputs = [
            (pkgs.python3.withPackages (ps: with ps; [
              click
              pure-python-adb
              uiautomator
            ]))
            fdroidcl
          ];
        };

        droidctlApp = { type = "app"; program = "${droidctl}/bin/droidctl"; };
        fdroidclApp = { type = "app"; program = "${fdroidcl}/bin/fdroidcl"; };
        apps = rec {
          droidctl = droidctlApp;
          fdroidcl = fdroidclApp;
          default = droidctl;
        };
        packages = { inherit uiautomator fdroidcl droidctl; };
      in
      {
        inherit apps packages devShell;
      }
    ));
}
