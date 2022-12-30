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

        # pyftype
        pyftype = pkgs.python3Packages.buildPythonPackage rec {
          pname = "pyftype";
          version = "1.2.3";
          src = pkgs.fetchgit {
            url = "https://gitee.com/kin9-0rz/pyftype.git";
            rev = "v${version}";
            sha256 = "sha256-gPXlrq9HHNiOxyqLIzYgBoEh/BLE+L9jcKZtuuM4icY=";
          };
          doCheck = false;
        };

        # pyelftools
        pyelftools_0_27 = pkgs.python3Packages.buildPythonPackage rec {
          pname = "pyelftools";
          version = "0.27";
          src = pkgs.python3Packages.fetchPypi {
            inherit pname version;
            sha256 = "sha256-zehU5mJ3TFRX1ojKQWFfZZQYe6cGevEBIy34iaa3pms=";
          };
          doCheck = false;
        };

        # apkutils
        apkutils = pkgs.python3Packages.buildPythonPackage rec {
          pname = "apkutils";
          version = "1.2.2";
          src = pkgs.python3Packages.fetchPypi {
            inherit pname version;
            sha256 = "sha256-Bd4wCmoheKerrGRANU6rcDQn6e3tnwfiJfPlY4uaq7Y=";
          };
          prePatch = ''
            substituteInPlace pyproject.toml \
              --replace 'cryptography = "^35.0.0"' 'cryptography = "^38.0.0"'
            substituteInPlace setup.py \
              --replace 'cryptography>=35.0.0,<36.0.0' \
                        'cryptography>=38.0.0,<39.0.0'
          '';
          propagatedBuildInputs = with pkgs.python3Packages; [
            pyelftools_0_27
            pyftype
            pygments
            beautifulsoup4
            cryptography
          ];
        };

        # adbutils
        adbutils = pkgs.python3Packages.buildPythonPackage rec {
          pname = "adbutils";
          version = "1.2.2";
          src = pkgs.fetchFromGitHub {
            owner = "openatx";
            repo = "adbutils";
            rev = version;
            sha256 = "sha256-VOp2Is8IrhUF4nPwpVtR+/ZjyQQsQ3gvCS2C2w3Sbeo";
          };
          propagatedBuildInputs = with pkgs.python3Packages; [
            pbr
            deprecation
            whichcraft
            requests
            apkutils
          ];
          PBR_VERSION = version;
        };

        # uiautomator2
        uiautomator2 = pkgs.python3Packages.buildPythonPackage rec {
          pname = "uiautomator2";
          version = "2.16.12";
          src = pkgs.fetchFromGitHub {
            owner = "openatx";
            repo = "uiautomator2";
            rev = version;
            sha256 = "sha256-j4BU6w7Lj6RalsFGL5qk45q2gkjv5vDcQC69pIwVqRk=";
          };
          prePatch = ''
            substituteInPlace requirements.txt \
              --replace 'packaging~=20.3' 'packaging~=21.1'
          '';
          propagatedBuildInputs = with pkgs.python3Packages; [
            adbutils
            pbr
            urllib3
            filelock
            packaging
          ];
          #doCheck = false;
          PBR_VERSION = version;
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
            uiautomator2
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
          uiautomator2
          pure-python-adb
        ]);

        devShell = pkgs.mkShell {
          buildInputs = [
            (pkgs.python3.withPackages (ps: with ps; [
              click
              pure-python-adb
              uiautomator2
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
        packages = {
          inherit uiautomator2 fdroidcl droidctl;
          default = droidctl;
        };
      in
      {
        inherit apps packages devShell;
      }
    ));
}
