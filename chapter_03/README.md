
> Ball of Mud pattern: as the application grows,
> if we're unable to prevent coupling between elements that have no cohesion, that
> coupling increases superlinearly until we are no longer able to effectively
> change our systems.

- Coupling: `SysA ---> SysB`
- Abstract: `SysA --> Abstraction --> SysB`


Our high-level code is coupled to low-level details, and it's making life hard.

- Think about what the code needs from the system. Distinct _responsibilities_.
- Simplifying Abstractions for each responsibilities (hide messy details)
- Isolate the clever part, be able to test it thoroughly without needing set up
- Separate _what_ we want to do from _how_ to do it
- "Given this _abstraction_ of a filesystem, what _abstraction_ of filesystem actions will happen?"
- FCIS: "Functional Core (no deps on ext state), Imperative Shell (input from outside)"
- Separate the stateful parts from logic (which takes simple structures, returns simple structures)

Test the lower-level function directly without low-level I/O details.

- "Edge to Edge" testing: invoke a whole system together, faking I/O
- Add an abstraction as new dependency into top level which can be invoked
- The real implementation does real I/O, but fake is just wrapper around abstraction
- Might want Fake (or test-double) to keep actions to check as Spy
- Monkeypatching/Mocks as a code-smell (keeps coupling)
