relationship between the beans. The only difference from previous exercises is the change in the JNDI name element tag for the Address home interface:

<local-jndi-name>AddressHomeLocal</local-jndi-name>

Because the Home interface for the Address is local, the tag is <local-jndi-name> rather than <jndi-name>.

The `weblogic-cmp-rdbms-jar.xml` descriptor file contains a number of new elements in this exercise. A detailed examination of the relationship elements will await until the next section.

The file contains a section mapping the Address `<camp-field>` attributes from the `ebj-jar.xml` file to the database columns in the `AUTHORITY` column to a new section related to the `USERID` column. The key values in this section are

```html

<weblogic-rdms-bean>

  <ejb-name>AddressLIB</ejb-name>

  <data-source-name>ltan-dataSource</data-source-name>

  <table-name>ADDRESS</table-name>

  <field-map>

    <cmp-field>id</cmp-field>

    <dbms-column>ID</dbms-column>

  </field-map>

  <field-map>

    <cmp-field>street</cmp-field>

    <dbms-column>STREET</dbms-column>

  </field-map>

  <field-map>

    <cmp-field>city</cmp-field>

    <dbms-column>CITY</dbms-column>

  </field-map>

  <field-map>

    <cmp-field>state</cmp-field>

    <dbms-column>STATE</dbms-column>

  </field-map>

  <field-map>

    <cmp-field>zip</cmp-field>

    <dbms-column>ZIP</dbms-column>

  </field-map>

  <!-- automatically generate the value of ID in the database on

inserts using sequence table -->

  <automatic-key-generation>

    <generator-type>NAMED_SEQUENCE_TABLE</generator-type>

    <generator-name>ADDRESS_SEQUENCE</generator-name>

    <key-cache-size>/Key-cache-size>

  </automatic-key-generation>

</weblogic-rdms-bean>

```