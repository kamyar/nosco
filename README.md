### Nosco v1.0- Smart Semantic Versioning Helper
====

**Nosco** - _[latin; in possession of knowledge, discern]_

Built to improve build process and solve version management problems. Follows Semantic Versioning
Scheme, has a simple and easy to understand YAML based configuration and module based extendable
structure.


#### USAGE
1. install PyYAML
    - `pip install pyyaml` (for config file)
2. prepare your \<your\_app\>.yaml  (see nosco.yaml for a sample config)
3. import nosco and create Nosco Object and retrieve your version. (see builder.py for an example)


#### Enhance
* You can write your own 'modules' and register them, you will be able to use them in 'generate' section of your config file and use generated values in version string.

#### TODO
- ~~Writing hg module~~
- Writing git module
- Add 'Build Certificate' generation
- Writing Misc. modules(machine arch., time, builder, etc.)
- More examples
- Test
- Integrate ruamel.yaml (for comment preservation, native ordered yaml support etc.)


#### CONTRIBUTE
- Contributions and improvements are most welcome, just send the pull request and explain your changes briefly. :)
