# Bonds

A bond drawn as a character inside running chemistry rather than as a bond site is the `'bond'` role of
`Sb`, in `references/catalogue/Symbols.md`.

## Bd — bond

One atom with bonds radiating from it. Molecules are built left to right along the baseline, and any
group of a bond site may hold a further bond site.

No properties beyond the two every equation structure has.

| Subgroup | Count | Holds |
| --- | --- | --- |
| `Gr` | 1 | The central atom. Required. |
| `Gr (t='uppr')` | 0 or 1 | The atom at the end of the upward bond. |
| `Gr (t='uplf')` | 0 or 1 | Upper left. |
| `Gr (t='uprt')` | 0 or 1 | Upper right. |
| `Gr (t='lowr')` | 0 or 1 | Downward. |
| `Gr (t='lwlf')` | 0 or 1 | Lower left. |
| `Gr (t='lwrt')` | 0 or 1 | Lower right. |

One or two `uint32[2]` data lists of pairs. The first pair list gives (group type, bond type) for each
bond, where a group type of `0` means the rightward bond, which has no group of its own. The bond
types are `'sing'`, `'doub'`, `'trip'`, `'hevy'`, `'wavy'`, `'part'`, `'prd1'`, `'prd2'`, `'prt1'`,
`'prt2'`, `'prt3'`, `'swgo'`, `'swgi'`, `'dwgo'` and `'dwgi'`; capitalising the first letter makes the
bond long, so `'Sing'` is a long single bond. The optional second pair list gives (group type, angle
type) with `'step'` for a steep angle and `'shal'` for a shallow one, and applies only to the four
diagonal directions.

```pie
// Radical Pie Equation

D
{
}
Gr
{
	Bg {}
	Bd
	{
		u32[2]{{'uppr','sing'},{0,'sing'}}
		Gr
		{
			Bg {}
			Sb (ro='chem') {s{"C"}}
		}
		Gr (t='uppr')
		{
			Bg {}
			Sb (ro='chem') {s{"H"}}
		}
	}
	Sb (ro='chem') {s{"OH"}}
}
```
