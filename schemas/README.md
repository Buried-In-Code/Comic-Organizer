# Schemas

The schemas are copied from their respective repos:

- [MetronInfo v1.0 - draft](https://github.com/Metron-Project/metroninfo/blob/8309db05b0825f39390125ec019a73ce34f03e0a/drafts/v1.0/MetronInfo.xsd)
- [ComicInfo v2.0](https://github.com/anansi-project/comicinfo/blob/9c3ebc1984711c83c71a729319b43d2f81d461e4/schema/v2.0/ComicInfo.xsd)

_The ComicInfo schema has been slightly adjusted to ignore field ordering_

```diff
<xs:complexType name="ComicInfo">
-  <xs:sequence>
+  <xs:all>
```
