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

        # cigam, needed by apkutils2
        cigam = pkgs.python3Packages.buildPythonPackage rec {
          pname = "cigam";
          version = "0.0.3";
          src = pkgs.python3Packages.fetchPypi {
            inherit pname version;
            sha256 = "sha256-j89l1zYfA3LFN4DoYTB6vR8RqUtiBPplO6PzgneCJ4M=";
            format = "wheel";
            dist = "py3";
            python = "py3";
          };
          format = "wheel";
        };

        # apkutils2, dependency of adbutils
        apkutils2 = pkgs.python3Packages.buildPythonPackage rec {
          pname = "apkutils2";
          version = "1.0.0";
          src = pkgs.python3Packages.fetchPypi {
            inherit pname version;
            sha256 = "sha256-xa6PhtPr7mpZ/AFNiFB3Qdfz+asYO6s0tE0BH+h4Zgs=";
          };
          propagatedBuildInputs = with pkgs.python3Packages; [
            cigam
            pyelftools
            xmltodict
            pillow
            retry
          ];
          doCheck = false;
        };

        # adbutils, dependency of uiautomator2
        adbutils = pkgs.python3Packages.buildPythonPackage rec {
          pname = "adbutils";
          version = "2.7.2";
          src = pkgs.python3Packages.fetchPypi {
            inherit pname version;
            sha256 = "sha256-7ooUSEUxgktorqRUyjR01n0eCPJUhH8+CNtKa3yWTbg=";
          };
          propagatedBuildInputs = with pkgs.python3Packages; [
            pbr
            deprecation
            whichcraft
            requests
            apkutils2
            setuptools
          ];
          PBR_VERSION = version;
          doCheck = false;
        };

        # uiautomator2
        uiautomator2 = pkgs.python3Packages.buildPythonPackage rec {
          pname = "uiautomator2";
          version = "3.1.0";
          format = "pyproject";
          src = pkgs.python3Packages.fetchPypi {
            inherit pname version;
            sha256 = "sha256-CJ1bWx1Gy4gCNvgX9jNdFPgp4Z7QJpjs0Wl6bBCwZMs=";
          };
          nativeBuildInputs = with pkgs.python3Packages; [
            poetry-core
            poetry-dynamic-versioning
          ];
          propagatedBuildInputs = with pkgs.python3Packages; [
            adbutils
            pbr
            urllib3
            filelock
            packaging
            lxml
            logzero
            progress
            cached-property
            six
            deprecated
          ];
          doCheck = false;
          #PBR_VERSION = version;
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

          vendorHash = "sha256-7ApthWHxD29p0U/6ygyrsNQsy2dVdbA/zE7D4DsuqoU=";
          doCheck = false;
        };

        droidctl = pkgs.python3Packages.buildPythonApplication {
          pname = "droidctl";
          version = "0.0.1";
          src = ./.;
          propagatedBuildInputs = with pkgs.python3Packages; [
            uiautomator2
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
        ]);

        devShell = pkgs.mkShell {
          buildInputs = [
            (pkgs.python3.withPackages (ps: with ps; [
              click
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
          inherit adbutils uiautomator2 fdroidcl droidctl;
          default = droidctl;
        };
      in
      {
        inherit apps packages devShell;
      }
    ));
}
