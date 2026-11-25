import Lake
open Lake DSL

package sunflower_base where
  leanOptions := #[
    ⟨`autoImplicit, false⟩,
    ⟨`relaxedAutoImplicit, false⟩
  ]

@[default_target]
lean_lib SunflowerBase where
  roots := #[`SunflowerBase]
